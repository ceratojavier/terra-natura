"""
Grilla de feed Instagram — pilares, hooks y captions (fuente JSON).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data" / "instagram_feed_grilla_junio_2026.json"


@lru_cache(maxsize=1)
def cargar_grilla() -> dict[str, Any]:
    if not _DATA.is_file():
        return {"publicaciones": [], "pilares": {}}
    return json.loads(_DATA.read_text(encoding="utf-8"))


def listar_publicaciones(*, mes: str | None = None) -> list[dict[str, Any]]:
    data = cargar_grilla()
    pubs = data.get("publicaciones") or []
    if mes:
        return [p for p in pubs if (p.get("mes") or "") == mes]
    return list(pubs)


def publicacion_por_orden(n: int) -> dict[str, Any] | None:
    for p in listar_publicaciones():
        if p.get("orden") == n:
            return p
    return None


_PERFIL = Path(__file__).resolve().parent.parent / "data" / "instagram_perfil_profesional.json"


@lru_cache(maxsize=1)
def cargar_perfil_profesional() -> dict[str, Any]:
    if not _PERFIL.is_file():
        return {}
    return json.loads(_PERFIL.read_text(encoding="utf-8"))


def kit_perfil_instagram() -> dict[str, Any]:
    """Bio, highlights, checklist y grilla de feed para armar perfil IG."""
    feed = cargar_grilla()
    perfil = cargar_perfil_profesional()
    return {
        "perfil": perfil,
        "pilares": feed.get("pilares"),
        "highlights_feed": feed.get("highlights"),
        "publicaciones": listar_publicaciones(),
        "docs": {
            "estrategia": "docs/INSTAGRAM_FEED_ESTRATEGIA_2026.md",
            "manychat": "docs/MANYCHAT_INSTAGRAM_FLUJO.md",
        },
    }
