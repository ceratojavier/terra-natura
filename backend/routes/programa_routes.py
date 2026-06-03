"""API — Centro de programa Terra Natura (estado y herramientas)."""
from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services import ama_service
from backend.services.calendario_importante_service import listar_importantes

router = APIRouter(prefix="/api/programa", tags=["Programa Terra Natura"])

_REPO = Path(__file__).resolve().parent.parent.parent
_MEDIA_FOTOS = _REPO / "archivos multimedia" / "fotos terra natura"
_MEDIA_ASSETS = _REPO / "ama" / "output" / "assets"


@router.get("/hoy")
def publicaciones_hoy():
    """Qué publicar hoy en cada red — vista diaria del dueño."""
    from backend.services.ama_service import vista_hoy_y_proximas

    return vista_hoy_y_proximas()


@router.get("/estado")
def estado_programa(db: Session = Depends(get_db)):
    dash = ama_service.dashboard()
    youtube_total = 0
    try:
        from backend.models.turismo import TurismoContenido

        youtube_total = (
            db.query(TurismoContenido)
            .filter(
                TurismoContenido.plataforma == "youtube",
                TurismoContenido.youtube_id.isnot(None),
            )
            .count()
        )
    except Exception:
        pass

    cola = ama_service.cola_publicacion_resumen()

    return {
        "nombre": "Terra Natura — Programa",
        "herramientas": {
            "python": bool(shutil.which("python") or shutil.which("py")),
            "ffmpeg": bool(shutil.which("ffmpeg")),
            "yt_dlp": bool(shutil.which("yt-dlp")),
        },
        "youtube_biblioteca": youtube_total,
        "cola_pendientes": cola.get("pendientes", 0),
        "calendario": {
            "total": dash.get("total_calendario", 0),
            "pendientes": dash.get("pendientes_aprobacion", 0),
            "hoy": dash.get("publicaciones_hoy", 0),
        },
        "mensaje": (
            "Todo listo para recolectar YouTube y generar videos editoriales."
            if youtube_total > 0
            else "Paso 1: recolectá videos de YouTube para la biblioteca B-roll."
        ),
    }


@router.get("/calendario-importantes")
def calendario_importantes(
    desde: date | None = Query(None, description="Default: hoy"),
    hasta: date | None = Query(None, description="Default: 31 marzo año que viene"),
    solo_confirmados: bool = Query(True, description="Solo feriados oficiales y eventos confirmados"),
    db: Session = Depends(get_db),
):
    """Agenda: feriados, puentes, vacaciones y eventos confirmados del rango."""
    return listar_importantes(desde=desde, hasta=hasta, db=db, solo_confirmados=solo_confirmados)


@router.post("/actualizar-agenda-eventos")
def actualizar_agenda_eventos(
    desde: date | None = Query(None),
    hasta: date | None = Query(None),
    descargar_fotos: bool = Query(True, description="Buscar y bajar banners en web si faltan"),
    db: Session = Depends(get_db),
):
    """Busca y fusiona eventos del período (fiestas recurrentes, seed, fuentes web)."""
    from ama.scrapers.event_hunter import actualizar_agenda

    from ama.scrapers.event_hunter import actualizar_agenda

    r = actualizar_agenda(desde=desde, hasta=hasta, db=db, scrape_web=descargar_fotos)
    if not descargar_fotos:
        r.setdefault("fotos_web", {"mensaje": "Descarga de fotos omitida (parámetro descargar_fotos=false)"})
    return r


@router.post("/descargar-fotos-eventos")
def descargar_fotos_eventos(
    desde: date | None = Query(None),
    hasta: date | None = Query(None),
    max: int = Query(15, ge=1, le=30, alias="max"),
):
    """Solo descarga imágenes faltantes (og:image / Wikimedia) — sin tocar agenda."""
    from ama.scrapers.event_image_fetcher import descargar_desde_confirmados_y_cache

    return descargar_desde_confirmados_y_cache(desde=desde, hasta=hasta, max_descargas=max)


@router.get("/media/{ruta:path}")
def servir_foto_multimedia(ruta: str):
    """Sirve JPG/PNG del inventario local (solo bajo fotos terra natura)."""
    base = _MEDIA_FOTOS.resolve()
    dest = (base / ruta).resolve()
    if not str(dest).startswith(str(base)) or not dest.is_file():
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    if dest.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        raise HTTPException(status_code=404, detail="Formato no permitido")
    return FileResponse(dest)


@router.get("/assets/{nombre}")
def servir_asset_ama(nombre: str):
    """Assets descargados (Kempes, etc.) en ama/output/assets."""
    base = _MEDIA_ASSETS.resolve()
    dest = (base / nombre).resolve()
    if not str(dest).startswith(str(base)) or not dest.is_file():
        raise HTTPException(status_code=404, detail="Asset no encontrado")
    return FileResponse(dest)


@router.get("/fuentes-agenda")
def fuentes_agenda():
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parent.parent.parent / "ama" / "data" / "fuentes_agenda_eventos.json"
    if not path.is_file():
        return {"fuentes": []}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@router.get("/calendario-importantes/export")
def export_calendario_importantes(
    desde: date | None = Query(None),
    hasta: date | None = Query(None),
    db: Session = Depends(get_db),
):
    import json
    from pathlib import Path

    data = listar_importantes(desde=desde, hasta=hasta, db=db)
    path = Path(__file__).resolve().parent.parent.parent / "ama" / "data" / "vista_previa_calendario.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return FileResponse(path, filename=path.name, media_type="application/json")
