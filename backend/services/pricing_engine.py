"""
Cotización según calendario comercial 2026 ($120k/$100k alta, $100k/$85k resto)
o modelo legacy (inflación + % baja). Ver `docs/TARIFAS_PROMOCIONES.md`.
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
PromoCodigo = Literal["ninguna", "3x2", "4x3", "5mas1", "4paga5", "auto"]


def _verano_midpoint(u: Unidad) -> float:
    mn = float(u.precio_verano_min or 0)
    mx = float(u.precio_verano_max or 0)
    if mn <= 0 and mx <= 0:
        return 0.0
    return (mn + mx) / 2.0


def _usar_calendario_comercial_2026(tp: dict) -> bool:
    if tp.get("modelo_tarifas") == "legacy_inflacion":
        return False
    return bool(tp.get("usar_calendario_comercial_2026", True))


def _temporada_noche_legacy(d: date) -> TemporadaNoche:
    if d.month in (1, 2):
        return "verano_alta"
    if d.month == 7:
        return "invierno_alta"
    return "media_baja"


def _temporada_noche_comercial(d: date) -> TemporadaNoche:
    if d.month in (1, 2):
        return "verano_alta"
    if d.month == 7:
        return "invierno_alta"
    return "media_baja"


def temporada_noche(d: date) -> TemporadaNoche:
    return _temporada_noche_legacy(d)


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
    bp = tp.get("base_precios") if isinstance(tp.get("base_precios"), dict) else {}
    if u.tipo == "alpina":
        raw = bp.get("alpina") or tp.get("base_verano_prom_alpina")
    else:
        raw = bp.get("suite") or tp.get("base_verano_prom_suite")
    if raw is not None and float(raw) > 0:
        return float(raw)
    return _verano_midpoint(u)


def _override_manual_por_fecha(
    raw_cfg: dict | None, unidad_id: str, fecha_iso: str
) -> float | None:
    if not isinstance(raw_cfg, dict):
        return None
    by_unit = raw_cfg.get(unidad_id)
    if not isinstance(by_unit, dict):
        return None
    raw = by_unit.get(fecha_iso)
    if isinstance(raw, dict):
        p = raw.get("precio_noche_ars")
        return float(p) if p is not None else None
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _en_ventana_invierno_2026(d: date) -> bool:
    from ama.engine import comercial_2026 as c26

    inv = c26.cargar().get("vacaciones_invierno_2026", {})
    v0, v1 = inv.get("ventana_general", ["", ""])
    return bool(v0 and v1 and v0 <= d.isoformat() <= v1)


def _estadia_en_invierno_2026(nights: list[date]) -> bool:
    return any(_en_ventana_invierno_2026(d) for d in nights)


def _todas_temporada_baja_comercial(nights: list[date]) -> bool:
    from ama.engine import comercial_2026 as c26

    return bool(nights) and all(c26.temporada_en_fecha(d) == "baja" for d in nights)


def resolver_promo_cotizacion(
    promo: str,
    nights: list[date],
    *,
    auto_promos: bool = True,
) -> PromoCodigo:
    """Normaliza promo solicitada; con `auto` o `ninguna`+auto_promos aplica reglas 2026."""
    if promo in ("3x2", "4x3", "5mas1", "4paga5"):
        return promo  # type: ignore[return-value]

    if promo not in ("ninguna", "auto") or not auto_promos or not nights:
        return "ninguna"

    n = len(nights)
    if _estadia_en_invierno_2026(nights) and n >= 6:
        return "5mas1"
    if _todas_temporada_baja_comercial(nights) and n >= 5:
        return "4paga5"
    return "ninguna"


def _precio_noche_comercial_2026(d: date, u: Unidad) -> tuple[float, TemporadaNoche, float, float]:
    from ama.engine import comercial_2026 as c26

    precio = float(c26.tarifa_orientativa_noche(d, u.tipo))
    temp = _temporada_noche_comercial(d)
    return precio, temp, 0.0, 1.0


def _precio_noche_legacy(
    d: date,
    u: Unidad,
    tp: dict,
    overrides_cfg: dict,
) -> tuple[float, TemporadaNoche, float, float]:
    temp_n = _temporada_noche_legacy(d)
    temporada_baja_cfg: dict = (
        tp["temporada_baja"] if isinstance(tp.get("temporada_baja"), dict) else {}
    )
    desc_lun_jue = float(
        temporada_baja_cfg.get("descuento_lunes_jueves_sobre_finde_baja", 0.15)
    )
    base_verano = _base_precio_unidad(tp, u)
    pct_baja = _pct_baja_unidad(tp, u)
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

    manual = _override_manual_por_fecha(overrides_cfg, u.id, d.isoformat())
    if manual is not None and manual > 0:
        precio_noche = manual

    return precio_noche, temp_n, coef["coeficiente_pct"], mult


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
        tp["temporada_baja"] if isinstance(tp.get("temporada_baja"), dict) else {}
    )
    pct_efectivo = float(tp.get("descuento_efectivo_sobre_total") or 0.10)
    overrides_row = config_service.get_config(db, "tarifas_overrides")
    overrides_cfg = overrides_row["valor"] if overrides_row else {}
    auto_promos = bool(tp.get("auto_promos_comercial_2026", True))
    usar_comercial = _usar_calendario_comercial_2026(tp)

    promo_efectiva = resolver_promo_cotizacion(
        promo, nights, auto_promos=auto_promos
    )

    desglose: list[NochePrecio] = []
    todas_baja_legacy = True

    for d in nights:
        if usar_comercial:
            precio_noche, temp_n, coef_pct, mult = _precio_noche_comercial_2026(d, u)
            manual = _override_manual_por_fecha(overrides_cfg, u.id, d.isoformat())
            if manual is not None and manual > 0:
                precio_noche = manual
            from ama.engine import comercial_2026 as c26

            if c26.temporada_en_fecha(d) != "baja":
                todas_baja_legacy = False
        else:
            precio_noche, temp_n, coef_pct, mult = _precio_noche_legacy(
                d, u, tp, overrides_cfg
            )
            if temp_n != "media_baja":
                todas_baja_legacy = False

        desglose.append(
            NochePrecio(
                fecha=d,
                es_finde_sem_baja=_es_finde_semana(d) and temp_n == "media_baja",
                temporada=temp_n,
                precio_noche=round(precio_noche, 2),
                coeficiente_inflacion_pct=coef_pct if coef_pct else None,
                multiplicador_inflacion=mult if mult != 1.0 else None,
            )
        )

    subtotal = sum(x.precio_noche for x in desglose)
    desc_promo = 0.0
    aplicadas: list[str] = []

    n = len(nights)

    if promo_efectiva == "5mas1" and n >= 6:
        desc_promo = min(x.precio_noche for x in desglose)
        aplicadas.append("invierno_5_mas_1_comercial_2026")
    elif promo_efectiva == "4paga5" and n >= 5:
        desc_promo = min(x.precio_noche for x in desglose)
        aplicadas.append("baja_4_paga_5_comercial_2026")
    elif promo_efectiva != "ninguna" and todas_baja_legacy:
        p3 = bool(temporada_baja_cfg.get("promo_3x2", True))
        p4 = bool(temporada_baja_cfg.get("promo_4x3", True))
        if promo_efectiva == "3x2" and n == 3 and p3:
            desc_promo = min(x.precio_noche for x in desglose)
            aplicadas.append("promo_3x2_temporada_baja")
        elif promo_efectiva == "4x3" and n == 4 and p4:
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
