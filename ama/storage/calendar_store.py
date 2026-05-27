"""
Calendario de publicaciones — JSON en ama/data/
"""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"
_CAL = _DATA / "publicaciones_calendario.json"
_CFG = _DATA / "ama_config.json"


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_config() -> dict:
    return _read_json(_CFG, {})


def set_config(patch: dict) -> dict:
    cfg = get_config()
    cfg.update(patch)
    _write_json(_CFG, cfg)
    return cfg


def list_publicaciones(
    desde: date | None = None,
    hasta: date | None = None,
    estado: str | None = None,
) -> list[dict]:
    rows = _read_json(_CAL, [])
    out: list[dict] = []
    for r in rows:
        fp = r.get("fecha_publicacion")
        if desde and fp and fp < desde.isoformat():
            continue
        if hasta and fp and fp > hasta.isoformat():
            continue
        if estado and r.get("estado") != estado:
            continue
        out.append(r)
    out.sort(key=lambda x: (x.get("fecha_publicacion") or "", x.get("creado_en") or ""))
    return out


def get_publicacion(pub_id: str) -> dict | None:
    for r in _read_json(_CAL, []):
        if r.get("id") == pub_id:
            return r
    return None


def crear_publicacion(data: dict) -> dict:
    rows = _read_json(_CAL, [])
    now = datetime.utcnow().isoformat() + "Z"
    row = {
        "id": str(uuid.uuid4()),
        "fecha_publicacion": data["fecha_publicacion"],
        "hora": data.get("hora", "10:00"),
        "canal": data.get("canal", "instagram"),
        "angulo": data.get("angulo", "parejas"),
        "titulo": data.get("titulo", ""),
        "copy": data.get("copy", ""),
        "hashtags": data.get("hashtags", []),
        "estado": data.get("estado", "borrador"),
        "notas": data.get("notas", ""),
        "video_ruta": data.get("video_ruta"),
        "objetivo": data.get("objetivo"),
        "formato": data.get("formato"),
        "guion": data.get("guion"),
        "assets": data.get("assets"),
        "brief_canva": data.get("brief_canva"),
        "whatsapp_url": data.get("whatsapp_url"),
        "creado_en": now,
        "actualizado_en": now,
    }
    rows.append(row)
    _write_json(_CAL, rows)
    return row


def actualizar_publicacion(pub_id: str, patch: dict) -> dict | None:
    rows = _read_json(_CAL, [])
    for i, r in enumerate(rows):
        if r.get("id") != pub_id:
            continue
        for k, v in patch.items():
            if v is not None:
                r[k] = v
        r["actualizado_en"] = datetime.utcnow().isoformat() + "Z"
        rows[i] = r
        _write_json(_CAL, rows)
        return r
    return None


def eliminar_publicacion(pub_id: str) -> bool:
    rows = _read_json(_CAL, [])
    new_rows = [r for r in rows if r.get("id") != pub_id]
    if len(new_rows) == len(rows):
        return False
    _write_json(_CAL, new_rows)
    return True
