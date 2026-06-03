"""
Calendario y estrategia comercial 2026 — Terra Natura (fuente: calendario_comercial_2026.json).
Usar en plan marketing, AMA, cotizaciones orientativas y WhatsApp.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data" / "calendario_comercial_2026.json"


@lru_cache(maxsize=1)
def cargar() -> dict[str, Any]:
    return json.loads(_DATA.read_text(encoding="utf-8"))


def temporada_en_fecha(d: date) -> str:
    """alta | media | baja (aproximación por mes + findes cargados)."""
    data = cargar()
    mes = d.month
    if mes in data["temporadas"]["alta"]["meses"]:
        return "alta"
    if mes in data["temporadas"]["media"]["meses"]:
        return "media"
    if mes in data["temporadas"]["baja"]["meses"]:
        return "baja"
    if any(_finde_cubre_fecha(f, d) for f in data.get("findes_largos_2026", [])):
        return "alta"
    inv = data.get("vacaciones_invierno_2026", {})
    v0, v1 = inv.get("ventana_general", ["", ""])
    if v0 and v1 and v0 <= d.isoformat() <= v1:
        return "alta"
    return "media"


def tarifa_orientativa_noche(d: date, unidad_tipo: str = "alpina") -> int:
    """ARS por noche según calendario comercial 2026 (orientativo; PMS puede override)."""
    data = cargar()
    t = temporada_en_fecha(d)
    bloque = (
        data["tarifas_ars_noche"]["alta_y_finde_largo_e_invierno"]
        if t == "alta"
        else data["tarifas_ars_noche"]["resto_ano"]
    )
    if unidad_tipo == "suite":
        return int(bloque["suite_2_3"])
    return int(bloque["alpina_4_5"])


def finde_largo_en_fecha(d: date) -> dict[str, Any] | None:
    """Si la fecha cae en ventana de un finde largo comercial 2026."""
    for f in cargar().get("findes_largos_2026", []):
        if _finde_cubre_fecha(f, d):
            return f
    return None


def _finde_cubre_fecha(f: dict, d: date) -> bool:
    ing = _parse(f.get("ingreso_recomendado"))
    sal = _parse(f.get("salida_recomendada") or f.get("fecha_feriado_fin"))
    if ing and sal:
        return ing <= d <= sal
    fer = _parse(f.get("fecha_feriado"))
    if fer and abs((d - fer).days) <= 3:
        return True
    fi = _parse(f.get("fecha_feriado_inicio"))
    ff = _parse(f.get("fecha_feriado_fin"))
    if fi and ff:
        return fi <= d <= ff
    return False


def _parse(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def promo_recomendada(
    d: date,
    *,
    noches: int = 2,
    en_invierno: bool | None = None,
) -> dict[str, Any]:
    """Promo sugerida para copy/WhatsApp; cotización PMS usa `pricing_engine` + este JSON."""
    data = cargar()
    if en_invierno is None:
        inv = data.get("vacaciones_invierno_2026", {})
        v0, v1 = inv.get("ventana_general", ["", ""])
        en_invierno = bool(v0 and v1 and v0 <= d.isoformat() <= v1)

    if en_invierno and noches >= 5:
        return {**data["vacaciones_invierno_2026"]["promo_oficial"], "prioridad": "maxima"}

    finde = finde_largo_en_fecha(d)
    if finde:
        return {
            "codigo": finde.get("id"),
            "nombre": finde.get("nombre"),
            "promo": finde.get("promo"),
            "noches_objetivo": finde.get("noches_objetivo", 3),
            "descontar": finde.get("descontar", False),
            "copy_angulo": finde.get("copy_angulo"),
        }

    if temporada_en_fecha(d) == "baja" and noches >= 4:
        return data["promociones_fijas"]["temporada_baja_4_paga_5"]

    if temporada_en_fecha(d) == "baja":
        return {
            "codigo": "escapada_romantica",
            "promo": "2 noches + detalle de bienvenida regional",
            "copy_angulo": "vender_descanso_no_cabana",
        }

    return {"codigo": "estandar", "promo": None, "beneficios": ["valor_antes_precio"]}


def estrategia_para_fecha(d: date) -> str:
    """Texto corto para AMA / plan marketing."""
    finde = finde_largo_en_fecha(d)
    if finde:
        if finde.get("descontar") is False:
            return (
                f"{finde['nombre']}: precio pleno, sin descuento agresivo. "
                f"Promo: {finde.get('promo', 'beneficio de estadía')}. "
                f"Objetivo {finde.get('noches_objetivo', 3)} noches."
            )
        return f"{finde['nombre']}: {finde.get('promo', 'promo de estadía')}."
    t = temporada_en_fecha(d)
    if t == "baja":
        return (
            "Temporada baja: empujar más noches (4 paga 5 lun–sáb AM). "
            "Vender tiempo y descanso, no solo precio."
        )
    if t == "alta":
        return "Alta demanda: urgencia suave + beneficios baratos; no regalar plata."
    return "Temporada media: valor percibido (check-out, detalle bienvenida)."


def dias_hasta_finde_largo(d: date) -> int | None:
    """Días hasta ingreso recomendado del próximo finde largo."""
    hoy = d
    prox: date | None = None
    for f in cargar().get("findes_largos_2026", []):
        ing = _parse(f.get("ingreso_recomendado"))
        if ing and ing >= hoy:
            if prox is None or ing < prox:
                prox = ing
    if prox:
        return (prox - hoy).days
    return None


def campana_invierno_activa(d: date) -> dict[str, Any] | None:
    """Ola de vacaciones julio 2026 más relevante para la fecha."""
    data = cargar().get("vacaciones_invierno_2026", {})
    for ola in data.get("olas", []):
        fechas = ola.get("fechas") or []
        if len(fechas) >= 2 and fechas[0] <= d.isoformat() <= fechas[1]:
            return ola
    v0, v1 = data.get("ventana_general", ["", ""])
    if v0 and v1 and v0 <= d.isoformat() <= v1:
        return {"id": "invierno_general", "prioridad": "alta"}
    return None
