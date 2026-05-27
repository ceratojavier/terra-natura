"""
Selección de fotos locales y referencias YouTube para piezas del calendario.
"""
from __future__ import annotations

import random
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent.parent
_MEDIA = _REPO / "archivos multimedia"
_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def listar_fotos(carpeta_rel: str | None, max_fotos: int = 6) -> list[str]:
    base = _MEDIA
    if carpeta_rel:
        base = _MEDIA / carpeta_rel.replace("\\", "/").strip("/")
    if not base.is_dir():
        base = _MEDIA
    fotos: list[Path] = []
    if base.is_dir():
        for p in sorted(base.rglob("*")):
            if p.suffix.lower() in _EXTS and p.is_file():
                fotos.append(p)
                if len(fotos) >= max_fotos * 3:
                    break
    if len(fotos) > max_fotos:
        random.shuffle(fotos)
        fotos = fotos[:max_fotos]
    return [str(p.relative_to(_REPO)).replace("\\", "/") for p in fotos]


def youtube_desde_db(db: Any | None, tema: str, max_items: int = 2) -> list[dict]:
    if db is None:
        return []
    try:
        from backend.models.turismo import TurismoContenido

        q = db.query(TurismoContenido).filter(
            TurismoContenido.youtube_id.isnot(None),
            TurismoContenido.plataforma == "youtube",
        )
        if tema:
            q = q.filter(TurismoContenido.titulo.ilike(f"%{tema[:20]}%"))
        rows = q.limit(max_items * 5).all()
        if not rows:
            rows = (
                db.query(TurismoContenido)
                .filter(TurismoContenido.youtube_id.isnot(None))
                .limit(max_items * 3)
                .all()
            )
        random.shuffle(rows)
        out = []
        for r in rows[:max_items]:
            yid = r.youtube_id
            out.append(
                {
                    "youtube_id": yid,
                    "titulo": r.titulo,
                    "url": f"https://www.youtube.com/watch?v={yid}",
                    "uso_sugerido": "clip_3_8_seg_inicio",
                    "thumbnail": r.thumbnail_url,
                }
            )
        return out
    except Exception:
        return []


def armar_assets(
    *,
    carpeta_media: str | None,
    db: Any | None = None,
    tema_youtube: str = "Bialet",
    incluir_video: bool = True,
) -> dict:
    fotos = listar_fotos(carpeta_media, max_fotos=6)
    yt = youtube_desde_db(db, tema_youtube, max_items=4) if incluir_video else []
    return {
        "fotos": fotos,
        "youtube_clips": yt,
        "carpeta_media": carpeta_media,
        "brief_video": _brief_video(fotos, yt),
    }


def _brief_video(fotos: list[str], yt: list[dict]) -> str:
    parts = []
    if fotos:
        parts.append(f"Slideshow/Reel con {len(fotos)} foto(s) local(es).")
    if yt:
        parts.append(
            "B-roll YouTube (fragmentos en montaje): "
            + ", ".join(y["titulo"][:40] for y in yt[:3])
        )
    if not parts:
        parts.append("Agregar fotos en archivos multimedia/ o recolectar YouTube.")
    return " ".join(parts)
