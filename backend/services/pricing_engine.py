"""
Cotización según temporada, config `tarifas_promociones` y precios de verano por unidad.
Ver `docs/TARIFAS_PROMOCIONES.md`.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

from sqlalchemy.orm import Session

from backend.models.unidad import Unidad
from backend.schemas.reserva import CotizarResponse, NochePrecio
from backend.services import config_service
from backend.services.inflacion_coeficiente_service import (
    coeficiente_mayor_interanual_o_anual_acumulado,
)

TemporadaNoche = Literal["verano_alta", "invierno_alta", "media_baja"]


def _verano_midpoint(u: Unidad) -> float:
    mn = float(u.precio_verano_min or 0)
    mx = float(u.precio_verano_max or 0)
    if mn <= 0 and mx <= 0:
        return 0.0
    return (mn + mx) / 2.0


def temporada_noche(d: date) -> TemporadaNoche:
    if d.month in (1, 2):
        return "verano_alta"
    if d.month == 7:
        return "invierno_alta"
    return "media_baja"


def noches_entre(check_in: date, check_out: date) -> list[date]:
    out: list[date] = []
    cur = check_in
    while cur < check_out:
        out.append(cur)
        cur += timedelta(days=1)
    return out


def _pct_baja_unidad(tp: dict, u: Unidad) -> float:
    raw = (
        tp.get("porcentaje_baja_sobre_verano_alpina")
        if u.tipo == "alpina"
        else tp.get("porcentaje_baja_sobre_verano_suite")
    )
    if raw is None:
        return 0.75
    return float(raw)


def _es_finde_semana(d: date) -> bool:
    return d.weekday() >= 4


def _base_precio_unidad(tp: dict, u: Unidad) -> float:
    """Precio base del último verano (sin inflación); fallback unidad DB."""
    bp = tp.get("base_precios") if isinstance(tp.get("base_precios"), dict) else {}
    if u.tipo == "alpina":
        raw = bp.get("alpina") or tp.get("base_verano_prom_alpina")
    else:
        raw = bp.get("suite") or tp.get("base_verano_prom_suite")
    if raw is not None and float(raw) > 0:
        return float(raw)
    return _verano_midpoint(u)


def cotizar(
    db: Session,
    u: Unidad,
    check_in: date,
    check_out: date,
    promo: str = "ninguna",
    aplicar_precio_efectivo: bool = False,
) -> CotizarResponse:
    nights = noches_entre(check_in, check_out)
    if not nights:
        raise ValueError("La estadía debe tener al menos una noche.")

    tp_row = config_service.get_config(db, "tarifas_promociones")
    raw_tp = tp_row["valor"] if tp_row else {}
    tp: dict = raw_tp if isinstance(raw_tp, dict) else {}
    temporada_baja_cfg: dict = (
        tp["temporada_baja"]
        if isinstance(tp.get("temporada_baja"), dict)
        else {}
    )
    desc_lun_jue = float(
        temporada_baja_cfg.get("descuento_lunes_jueves_sobre_finde_baja", 0.15)
    )
    pct_efectivo = float(tp.get("descuento_efectivo_sobre_total") or 0.10)

    base_verano = _base_precio_unidad(tp, u)
    pct_baja = _pct_baja_unidad(tp, u)

    desglose: list[NochePrecio] = []
    todas_baja = True

    for d in nights:
        temp_n = temporada_noche(d)
        if temp_n != "media_baja":
            todas_baja = False

        es_finde_flag = False
        if temp_n == "media_baja" and _es_finde_semana(d):
            es_finde_flag = True

        coef = coeficiente_mayor_interanual_o_anual_acumulado(d)
        mult = coef["multiplicador"]
        precio_ajustado = base_verano * mult

        if temp_n in ("verano_alta", "invierno_alta"):
            precio_noche = precio_ajustado
        else:
            base_finde = precio_ajustado * pct_baja
            if _es_finde_semana(d):
                precio_noche = base_finde
            else:
                precio_noche = base_finde * (1.0 - desc_lun_jue)

        desglose.append(
            NochePrecio(
                fecha=d,
                es_finde_sem_baja=es_finde_flag,
                temporada=temp_n,
                precio_noche=round(precio_noche, 2),
                coeficiente_inflacion_pct=coef["coeficiente_pct"],
                multiplicador_inflacion=coef["multiplicador"],
            )
        )

    subtotal = sum(x.precio_noche for x in desglose)
    desc_promo = 0.0
    aplicadas: list[str] = []

    if promo != "ninguna" and todas_baja:
        p3 = bool(temporada_baja_cfg.get("promo_3x2", True))
        p4 = bool(temporada_baja_cfg.get("promo_4x3", True))
        n = len(nights)
        if promo == "3x2" and n == 3 and p3:
            desc_promo = min(x.precio_noche for x in desglose)
            aplicadas.append("promo_3x2_temporada_baja")
        elif promo == "4x3" and n == 4 and p4:
            desc_promo = min(x.precio_noche for x in desglose)
            aplicadas.append("promo_4x3_temporada_baja")

    post_promo = max(0.0, subtotal - desc_promo)
    desc_efectivo = post_promo * pct_efectivo if aplicar_precio_efectivo else 0.0
    total = max(0.0, post_promo - desc_efectivo)

    return CotizarResponse(
        unidad_id=u.id,
        noches=len(nights),
        desglose=desglose,
        subtotal_sin_promo=round(subtotal, 2),
        descuento_promo=round(desc_promo, 2),
        descuento_efectivo=round(desc_efectivo, 2),
        total=round(total, 2),
        promos_aplicadas=aplicadas,
    )
