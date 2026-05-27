"""
AMA — Marketing: calendario, copy, video, configuración.
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.schemas.ama import (
    ConfigAmaPatch,
    GenerarCalendario90In,
    GenerarCalendarioEditorialIn,
    GenerarCopyIn,
    GenerarSemanaIn,
    PublicacionCreate,
    PublicacionPatch,
    VideoDesdeGuionIn,
    VideoLoteCalendarioIn,
    VideoSlideshowIn,
)
from pathlib import Path

from backend.services import ama_service
from ama.storage import calendar_store

router = APIRouter(prefix="/api/ama", tags=["AMA Marketing"])

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@router.get("/dashboard")
def ama_dashboard():
    return ama_service.dashboard()


@router.get("/estado")
def ama_estado():
    d = ama_service.dashboard()
    return {
        "nombre": "AMA — Marketing Terra Natura",
        "fase": "MVP activo (calendario + copy + video local)",
        "modo_publicacion": d["modo_publicacion"],
        "modulos": {
            "calendario_publicaciones": {"estado": "activo"},
            "generador_copy": {"estado": "activo"},
            "generador_video": {"estado": "activo", "nota": "MoviePy opcional"},
            "publicador_meta": {"estado": "pendiente", "nota": "Requiere tokens Meta"},
            "whatsapp_api": {"estado": "pendiente"},
        },
        "mensaje": d["mensaje"],
    }


@router.get("/config")
def get_config():
    return calendar_store.get_config()


@router.patch("/config")
def patch_config(body: ConfigAmaPatch):
    patch = body.model_dump(exclude_unset=True)
    return calendar_store.set_config(patch)


@router.get("/calendario")
def listar_calendario(
    desde: date | None = Query(None),
    hasta: date | None = Query(None),
    estado: str | None = Query(None),
):
    return {
        "publicaciones": calendar_store.list_publicaciones(desde=desde, hasta=hasta, estado=estado)
    }


@router.post("/calendario")
def crear_en_calendario(body: PublicacionCreate):
    data = body.model_dump()
    data["fecha_publicacion"] = body.fecha_publicacion.isoformat()
    if "texto" in data:
        data["copy"] = data.pop("texto")
    return calendar_store.crear_publicacion(data)


@router.patch("/calendario/{pub_id}")
def actualizar_calendario(pub_id: str, body: PublicacionPatch):
    patch = body.model_dump(exclude_unset=True)
    if "fecha_publicacion" in patch and patch["fecha_publicacion"]:
        patch["fecha_publicacion"] = patch["fecha_publicacion"].isoformat()
    if "texto" in patch:
        patch["copy"] = patch.pop("texto")
    row = calendar_store.actualizar_publicacion(pub_id, patch)
    if not row:
        raise HTTPException(404, "Publicación no encontrada")
    return row


@router.delete("/calendario/{pub_id}")
def borrar_calendario(pub_id: str):
    if not calendar_store.eliminar_publicacion(pub_id):
        raise HTTPException(404, "Publicación no encontrada")
    return {"ok": True}


@router.post("/generar-copy")
def api_generar_copy(body: GenerarCopyIn):
    return ama_service.generar_copy_api(**body.model_dump())


@router.post("/generar-semana")
def api_generar_semana(body: GenerarSemanaIn):
    return ama_service.generar_semana_api(body.desde, body.dias, body.guardar_en_calendario)


@router.post("/generar-calendario-editorial")
def api_generar_calendario_editorial(
    body: GenerarCalendarioEditorialIn, db: Session = Depends(get_db)
):
    return ama_service.generar_calendario_editorial_api(
        desde=body.desde,
        hasta=body.hasta,
        dias=body.dias,
        guardar=body.guardar_en_calendario,
        reemplazar_borradores=body.reemplazar_borradores_en_rango,
        db=db,
    )


@router.post("/generar-calendario-90")
def api_generar_calendario_90(body: GenerarCalendario90In, db: Session = Depends(get_db)):
    return ama_service.generar_calendario_90_api(
        body.desde,
        body.dias,
        body.guardar_en_calendario,
        body.reemplazar_borradores_en_rango,
        db=db,
    )


@router.get("/calendario-90/export")
def export_calendario_90():
    path = _REPO_ROOT / "ama" / "data" / "calendario_90_ultimo.json"
    if not path.is_file():
        raise HTTPException(404, "Generá primero el calendario 90 días desde /marketing")
    return FileResponse(path, filename=path.name, media_type="application/json")


@router.get("/calendario/alertas-campana")
def alertas_campana(dias: int = Query(90, ge=7, le=180)):
    from ama.engine.calendar_context import alertas_campana_proximas

    return {"alertas": alertas_campana_proximas(dias=dias)}


@router.post("/video/slideshow")
def api_video(body: VideoSlideshowIn):
    return ama_service.video_slideshow_api(**body.model_dump())


@router.post("/video/editorial")
def api_video_editorial(body: VideoDesdeGuionIn, db: Session = Depends(get_db)):
    """Video cinematográfico: B-roll YouTube + fotos complejo + marca."""
    return ama_service.video_desde_guion_api(
        pub_id=body.pub_id,
        guion=body.guion,
        assets=body.assets,
        db=db,
    )


@router.post("/video/lote-calendario")
def api_video_lote(body: VideoLoteCalendarioIn, db: Session = Depends(get_db)):
    """Genera videos para próximos posts reel sin video (máx N por llamada)."""
    return ama_service.video_lote_calendario_api(body.dias, body.max_videos, db=db)


@router.get("/video/archivo")
def descargar_video(ruta: str = Query(..., description="Ruta relativa devuelta por generar video")):
    if ".." in ruta or ruta.startswith("/"):
        raise HTTPException(400, "Ruta inválida")
    path = _REPO_ROOT / ruta.replace("/", "\\")
    if not path.is_file() or ("output" not in str(path) and "videos marketing" not in str(path)):
        raise HTTPException(404, "Video no encontrado")
    return FileResponse(path, media_type="video/mp4", filename=path.name)


@router.post("/whatsapp/borrador-respuesta")
def borrador_whatsapp(mensaje_cliente: str = Query(..., min_length=1)):
    from ama.chat.responder import responder_consulta_texto_plano

    r = responder_consulta_texto_plano(mensaje_cliente)
    gen = ama_service.generar_copy_api(angulo="parejas", canal="whatsapp_status")
    return {
        "sugerencia_corta": r.texto,
        "escalar_humano": r.debe_escalar_humano,
        "motivo_escalado": r.motivo_escalado,
        "plantilla_promo": gen["copy"][:500],
        "whatsapp_url": gen["whatsapp_url"],
    }
