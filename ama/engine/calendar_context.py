"""
Contexto calendario: feriados, puentes, vacaciones invierno, eventos turismo.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> dict:
    p = _DATA / name
    if not p.is_file():
        return {}
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def feriados_nacionales() -> list[dict]:
    pu = _load("feriados_puentes_ar.json")
    if pu.get("feriados_nacionales"):
        return pu["feriados_nacionales"]
    return _load("feriados_ar.json") if (_DATA / "feriados_ar.json").is_file() else []


def fines_de_semana_largo() -> list[dict]:
    return _load("feriados_puentes_ar.json").get("fines_de_semana_largo", [])


def vacaciones_invierno() -> list[dict]:
    return _load("vacaciones_invierno_provincias.json").get("vacaciones_invierno", [])


def reglas_editoriales() -> dict:
    return _load("calendario_editorial_reglas.json")


def evento_en_fecha(d: date) -> dict | None:
    """Devuelve finde largo o feriado que cae en d."""
    iso = d.isoformat()
    for pu in fines_de_semana_largo():
        try:
            ini = date.fromisoformat(pu["fecha_inicio"])
            fin = date.fromisoformat(pu["fecha_fin"])
        except (KeyError, ValueError):
            continue
        if ini <= d <= fin:
            return {"tipo": "finde_largo", **pu}
    for f in feriados_nacionales():
        if f.get("fecha") == iso:
            return {"tipo": "feriado", **f}
    for v in vacaciones_invierno():
        try:
            ini = date.fromisoformat(v["fecha_inicio"])
            fin = date.fromisoformat(v["fecha_fin"])
        except (KeyError, ValueError):
            continue
        if ini <= d <= fin:
            return {"tipo": "vacaciones_invierno", **v}
    return None


def alertas_campana_proximas(desde: date | None = None, dias: int = 90) -> list[dict]:
    """Ventanas para CTA según feriados/puentes."""
    hoy = desde or date.today()
    lim = hoy + timedelta(days=dias)
    out: list[dict] = []
    ventanas = _load("feriados_puentes_ar.json").get("ventanas_campana_dias_antes", {})
    dias_puente = ventanas.get("puente", [60, 30, 14, 7])

    for pu in fines_de_semana_largo():
        try:
            ini = date.fromisoformat(pu["fecha_inicio"])
        except (KeyError, ValueError):
            continue
        for d_antes in dias_puente:
            disparo = ini - timedelta(days=d_antes)
            if hoy <= disparo <= lim:
                out.append(
                    {
                        "disparo": disparo.isoformat(),
                        "evento": pu.get("nombre"),
                        "fecha_evento": pu["fecha_inicio"],
                        "dias_antes": d_antes,
                        "tipo": "recordatorio_campana",
                        "mensaje": f"Faltan {d_antes} días para armar campaña: {pu.get('nombre')}",
                        "copy_hook": pu.get("copy_hook"),
                    }
                )
    return sorted(out, key=lambda x: x["disparo"])


def eventos_turismo_db(db: Any, desde: date, hasta: date) -> list[dict]:
    """Eventos de grilla turismo en rango (si hay DB)."""
    try:
        from backend.models.turismo import TurismoEvento

        rows = (
            db.query(TurismoEvento)
            .filter(TurismoEvento.activo.is_(True))
            .all()
        )
        out = []
        for ev in rows:
            fd = getattr(ev, "fecha_inicio", None)
            if not fd:
                continue
            if isinstance(fd, str):
                try:
                    fd = date.fromisoformat(fd[:10])
                except ValueError:
                    continue
            if desde <= fd <= hasta:
                out.append(
                    {
                        "nombre": ev.nombre,
                        "fecha": fd.isoformat(),
                        "localidad": ev.localidad,
                        "tags": ev.tags or [],
                    }
                )
        return out
    except Exception:
        return []
