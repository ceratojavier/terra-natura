"""
Plan de publicaciones por tipo de evento y buyer persona — matriz en JSON.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

_MATRIZ = Path(__file__).resolve().parent.parent / "data" / "matriz_publicaciones_evento_persona.json"


def _load_matriz() -> dict:
    if not _MATRIZ.is_file():
        return {}
    return json.loads(_MATRIZ.read_text(encoding="utf-8"))


def _texto(ev: dict) -> str:
    tags = ev.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    return " ".join(
        [
            str(ev.get("nombre") or ""),
            str(ev.get("localidad") or ""),
            str(ev.get("categoria") or ""),
            str(ev.get("tipo") or ""),
            " ".join(str(t) for t in tags),
        ]
    ).lower()


def clasificar_tipo_evento(ev: dict) -> str:
    t = _texto(ev)
    mat = _load_matriz()
    # Orden: reglas específicas (texto) antes que categoría genérica
    for tipo_id, defn in (mat.get("tipos_evento") or {}).items():
        for regla in defn.get("detectar") or []:
            if regla.startswith("tipo:"):
                if ev.get("tipo") == regla.split(":", 1)[1]:
                    return tipo_id
            elif regla.lower() in t and not regla.startswith("categoria:"):
                return tipo_id
    for tipo_id, defn in (mat.get("tipos_evento") or {}).items():
        for regla in defn.get("detectar") or []:
            if regla.startswith("categoria:"):
                if (ev.get("categoria") or "") == regla.split(":", 1)[1]:
                    return tipo_id
    if ev.get("tipo") in ("puente", "finde_largo", "feriado_nacional"):
        return "finde_largo_puente"
    return (mat.get("fallback") or {}).get("tipo") or "generico_evento"


def plan_publicaciones(ev: dict) -> dict[str, Any]:
    """
    Devuelve buyer personas objetivo + cronograma de piezas sugeridas.
    """
    mat = _load_matriz()
    personas_def = mat.get("buyer_personas") or {}
    tipo_id = clasificar_tipo_evento(ev)
    defn = (mat.get("tipos_evento") or {}).get(tipo_id) or mat.get("fallback") or {}

    fi_s = ev.get("fecha_inicio") or ev.get("fecha")
    try:
        fi = date.fromisoformat(str(fi_s)[:10]) if fi_s else None
    except ValueError:
        fi = None

    personas_ids = defn.get("personas") or ["pareja_escapada"]
    personas_out = [
        {"id": pid, **(personas_def.get(pid) or {"label": pid})}
        for pid in personas_ids
    ]

    piezas = []
    for pub in defn.get("publicaciones") or []:
        dias = int(pub.get("dias_antes") or 30)
        fecha_pub = (fi - timedelta(days=dias)).isoformat() if fi else None
        piezas.append(
            {
                **pub,
                "fecha_publicacion_sugerida": fecha_pub,
                "tipo_evento": tipo_id,
                "personas_objetivo": personas_ids,
            }
        )

    piezas.sort(key=lambda x: x.get("fecha_publicacion_sugerida") or "9999")

    return {
        "tipo_evento": tipo_id,
        "buyer_personas": personas_out,
        "publicaciones": piezas,
        "evento": ev.get("nombre"),
        "fecha_evento": fi_s,
    }
