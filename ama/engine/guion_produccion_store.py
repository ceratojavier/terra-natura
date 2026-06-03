"""Persistencia de marcas de usuario (YouTube inicio/fin, id) por pieza del calendario."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DIR = Path(__file__).resolve().parent.parent / "data" / "guiones_produccion"


def _safe_id(pieza_id: str) -> str:
    return re.sub(r"[^\w\-.|]", "_", pieza_id)[:120]


def _path(pieza_id: str) -> Path:
    _DIR.mkdir(parents=True, exist_ok=True)
    return _DIR / f"{_safe_id(pieza_id)}.json"


def cargar(pieza_id: str) -> dict[str, Any]:
    p = _path(pieza_id)
    if not p.is_file():
        return {"pieza_id": pieza_id, "escenas": {}}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"pieza_id": pieza_id, "escenas": {}}


def guardar(pieza_id: str, data: dict[str, Any]) -> dict[str, Any]:
    data["pieza_id"] = pieza_id
    data["actualizado_en"] = datetime.now(timezone.utc).isoformat()
    _path(pieza_id).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def actualizar_escena(
    pieza_id: str,
    numero: int,
    *,
    youtube_id: str | None = None,
    youtube_url: str | None = None,
    youtube_inicio_seg: float | None = None,
    youtube_fin_seg: float | None = None,
    foto_ruta: str | None = None,
) -> dict[str, Any]:
    data = cargar(pieza_id)
    escenas = data.setdefault("escenas", {})
    key = str(numero)
    row = escenas.get(key, {})
    if youtube_id is not None:
        row["youtube_id"] = youtube_id.strip()
    if youtube_url is not None:
        row["youtube_url"] = youtube_url.strip()
    if youtube_inicio_seg is not None:
        row["youtube_inicio_seg"] = float(youtube_inicio_seg)
    if youtube_fin_seg is not None:
        row["youtube_fin_seg"] = float(youtube_fin_seg)
    if foto_ruta is not None:
        row["foto_ruta"] = foto_ruta.strip()
    escenas[key] = row
    return guardar(pieza_id, data)


def fusionar_marcas_en_escenas(escenas: list[dict], pieza_id: str) -> list[dict]:
    marcas = cargar(pieza_id).get("escenas") or {}
    out = []
    for esc in escenas:
        e = dict(esc)
        m = marcas.get(str(e.get("numero", ""))) or {}
        for k in (
            "youtube_id",
            "youtube_url",
            "youtube_inicio_seg",
            "youtube_fin_seg",
            "foto_ruta",
        ):
            if m.get(k) is not None:
                e[k] = m[k]
        if e.get("tipo") in ("broll_youtube", "clip_youtube"):
            if e.get("youtube_id") and e.get("youtube_inicio_seg") is not None:
                e["estado"] = "listo"
            else:
                e["estado"] = "pendiente_youtube"
        elif e.get("tipo") == "foto":
            e["estado"] = "listo" if e.get("foto_ruta") or e.get("fuente") else "pendiente_foto"
        out.append(e)
    return out
