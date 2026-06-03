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
    PipelineDiaIn,
    VideoDesdeGuionIn,
    VideoLoteCalendarioIn,
    VideoSlideshowIn,
    GuionProduccionPiezaIn,
    GuionProduccionEscenaIn,
    PiezaEnviarPublicacionesIn,
    ScannerAvisoIn,
    ScannerDescartarIn,
)
from pathlib import Path

from backend.services import ama_service
from ama.storage import calendar_store

router = APIRouter(prefix="/api/ama", tags=["AMA Marketing"])

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@router.get("/hoy")
def api_pantalla_hoy(db: Session = Depends(get_db)):
    """Pantalla principal del dueño — lenguaje simple."""
    return ama_service.pantalla_hoy_api(db=db)


@router.get("/estrategia-anual")
def api_estrategia_anual():
    """Programa 2026, efemérides, campañas pago, reglas editoriales."""
    return ama_service.estrategia_anual_api()


@router.get("/director/semana")
def api_director_semana(
    ref: date | None = Query(None, description="Fecha de referencia (default: hoy)"),
    db: Session = Depends(get_db),
):
    """Plan semanal del Director — qué publicar y por qué (sin copy hasta producir)."""
    return ama_service.director_semanal_api(ref=ref, db=db)


@router.post("/director/semana/producir")
def api_director_semana_producir(
    ref: date | None = Query(None),
    db: Session = Depends(get_db),
):
    """Genera copy/guion solo para las piezas de la semana planificada (sin encolar)."""
    return ama_service.director_semanal_producir_api(ref=ref, db=db)


@router.post("/director/semana/ejecutar")
def api_director_semana_ejecutar(
    ref: date | None = Query(None),
    solo_hoy: bool = Query(False, description="Solo piezas de hoy (legacy preparar-contenido-hoy)"),
    render_video: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Único flujo operativo: produce, encola Publicaciones y video del reel de hoy."""
    return ama_service.director_ejecutar_plan_api(
        ref=ref,
        db=db,
        render_video_hoy=render_video,
        solo_hoy=solo_hoy,
    )


@router.get("/director/contexto-pms")
def api_director_contexto_pms(
    ref: date | None = Query(None),
    db: Session = Depends(get_db),
):
    """Ocupación y huecos de la semana — insumo del Director."""
    from ama.engine.director_semanal import fin_semana, inicio_semana
    from ama.engine.pms_contexto import analizar_semana_pms

    d = ref or date.today()
    return analizar_semana_pms(inicio_semana(d), fin_semana(d), db=db, hoy=date.today())


@router.get("/scanner/bandeja")
def api_scanner_bandeja():
    """Eventos detectados o avisados — pendientes de incorporar al radar."""
    return ama_service.scanner_bandeja_api()


@router.post("/scanner/escanear")
def api_scanner_escanear(
    actualizar_fuentes: bool = Query(False),
    db: Session = Depends(get_db),
):
    """Busca novedades en la agenda vs confirmados (no produce copy)."""
    return ama_service.scanner_escanear_api(db=db, actualizar_fuentes=actualizar_fuentes)


@router.post("/scanner/analizar")
def api_scanner_analizar(body: ScannerAvisoIn):
    """Analiza texto pegado por el dueño antes de incorporar."""
    return ama_service.scanner_analizar_api(body.texto, guardar=body.guardar)


@router.post("/scanner/aviso")
def api_scanner_aviso(body: ScannerAvisoIn):
    """Registra aviso manual en la bandeja (si conviene)."""
    return ama_service.scanner_aviso_api(body.texto)


@router.post("/scanner/incorporar/{item_id}")
def api_scanner_incorporar(item_id: str):
    """Pasa evento a confirmados — el Director Semanal decide cuándo producir."""
    result = ama_service.scanner_incorporar_api(item_id)
    if not result.get("ok"):
        raise HTTPException(400, result.get("mensaje") or result.get("error"))
    return result


@router.post("/scanner/descartar/{item_id}")
def api_scanner_descartar(item_id: str, body: ScannerDescartarIn | None = None):
    result = ama_service.scanner_descartar_api(item_id, motivo=(body.motivo if body else ""))
    if not result.get("ok"):
        raise HTTPException(404, "Evento no encontrado")
    return result


@router.get("/plan-marketing")
def api_plan_marketing(
    anio: int | None = Query(None, ge=2024, le=2030),
    mes: int | None = Query(None, ge=1, le=12),
    desarrollar_completo: bool = Query(False, description="Genera guion+copy de todas las piezas del año (lento)"),
    db: Session = Depends(get_db),
):
    return ama_service.plan_marketing_api(
        db=db,
        anio=anio,
        mes=mes,
        desarrollar_completo=desarrollar_completo,
    )


@router.get("/plan-marketing/hito/{hito_id}")
def api_plan_hito(hito_id: str, db: Session = Depends(get_db)):
    try:
        return ama_service.plan_hito_api(hito_id, db=db)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


@router.get("/plan-marketing/pieza/{hito_id}/{pieza_id}")
def api_plan_pieza(hito_id: str, pieza_id: str, db: Session = Depends(get_db)):
    try:
        return ama_service.plan_pieza_api(hito_id, pieza_id, db=db)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


@router.post("/guion-produccion/generar")
def api_guion_produccion_generar(body: GuionProduccionPiezaIn, db: Session = Depends(get_db)):
    """Escenas detalladas + títulos para buscar en YouTube + fotos justificadas."""
    try:
        return ama_service.guion_produccion_generar_api(body.hito_id, body.pieza_id, db=db)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


@router.patch("/guion-produccion/escena")
def api_guion_produccion_escena(body: GuionProduccionEscenaIn, db: Session = Depends(get_db)):
    """Guardá ID YouTube y segundo inicio/fin que marcás en el video."""
    try:
        return ama_service.guion_produccion_escena_api(
            body.hito_id,
            body.pieza_id,
            body.numero,
            youtube_id=body.youtube_id,
            youtube_url=body.youtube_url,
            youtube_inicio_seg=body.youtube_inicio_seg,
            youtube_fin_seg=body.youtube_fin_seg,
            foto_ruta=body.foto_ruta,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


@router.post("/guion-produccion/render")
def api_guion_produccion_render(body: GuionProduccionPiezaIn, db: Session = Depends(get_db)):
    """Arma el MP4 cuando todas las escenas YouTube están marcadas."""
    result = ama_service.guion_produccion_render_api(body.hito_id, body.pieza_id, db=db)
    if not result.get("ok"):
        raise HTTPException(400, result.get("error") or "No se pudo generar el video")
    return result


@router.post("/pieza/enviar-publicaciones")
def api_pieza_enviar_publicaciones(
    body: PiezaEnviarPublicacionesIn, db: Session = Depends(get_db)
):
    """Calendario/plan → cola Publicaciones (mismo copy y video del guion)."""
    try:
        return ama_service.pieza_enviar_publicaciones_api(
            body.hito_id,
            body.pieza_id,
            video_ruta=body.video_ruta,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/instagram-feed")
def api_instagram_feed(mes: str | None = Query(None, description="Ej. 2026-06")):
    """Grilla de feed IG (pilares, hooks, captions) — `ama/data/instagram_feed_grilla_junio_2026.json`."""
    from ama.engine.instagram_feed import cargar_grilla, listar_publicaciones

    data = cargar_grilla()
    pubs = listar_publicaciones(mes=mes)
    return {"pilares": data.get("pilares"), "highlights": data.get("highlights"), "publicaciones": pubs}


@router.get("/instagram-perfil")
def api_instagram_perfil():
    """Kit perfil profesional: bio, checklist, highlights, grilla de posts."""
    from ama.engine.instagram_feed import kit_perfil_instagram

    return kit_perfil_instagram()


@router.get("/calendario-visual")
def api_calendario_visual(
    anio: int | None = Query(None, ge=2024, le=2030),
    mes: int | None = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
):
    """Grilla mensual: hitos en rango + publicaciones por día (IG/WA)."""
    return ama_service.calendario_visual_api(anio=anio, mes=mes, db=db)


@router.post("/plan-marketing/sincronizar")
def api_plan_sincronizar(db: Session = Depends(get_db)):
    from ama.engine.plan_marketing_unificado import sincronizar_plan_cache

    return sincronizar_plan_cache(db=db)


@router.post("/preparar-contenido-hoy")
def api_preparar_hoy(db: Session = Depends(get_db)):
    """Deprecated — usa POST /api/ama/director/semana/ejecutar?solo_hoy=true."""
    return ama_service.preparar_contenido_hoy_api(db=db)


@router.post("/publicar/{pub_id}")
def api_publicar(pub_id: str):
    try:
        return ama_service.publicar_en_instagram_api(pub_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


@router.get("/conexiones")
def api_conexiones():
    from ama.publishers.meta_publisher import estado_conexion_meta
    from ama.video.toolkit.connectors.registry import estado_todos

    return {
        "instagram": estado_conexion_meta(),
        "video_ia": estado_todos(),
    }


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
            "generador_video": {"estado": "activo", "nota": "MoviePy + FFmpeg + CapCut brief"},
            "pipeline_diario": {
                "estado": "delegado",
                "nota": "Redirige al Director Semanal — POST /api/ama/director/semana/ejecutar",
            },
            "herramientas_video_ia": {"estado": "activo", "nota": "Catálogo gratis en /api/ama/video/herramientas"},
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


@router.post("/video/pipeline/dia")
def api_pipeline_dia(body: PipelineDiaIn, db: Session = Depends(get_db)):
    """Pipeline: plan editorial → guion → video local → brief CapCut → cola publicación."""
    return ama_service.pipeline_dia_api(
        body.fecha,
        render_video=body.render_video,
        guardar_calendario=body.guardar_calendario,
        carpeta_media=body.carpeta_media,
        db=db,
    )


@router.get("/video/herramientas")
def api_video_herramientas():
    from ama.video.toolkit.ai_video_catalog import listar_herramientas, listar_por_region, recomendar_stack

    return {
        "herramientas": listar_herramientas(),
        "por_region": listar_por_region(),
        "stack_recomendado": recomendar_stack("reel_hospitality"),
    }


@router.get("/video/ia/catalogo")
def api_ia_catalogo():
    from ama.video.toolkit.ai_video_catalog import listar_herramientas, listar_por_region

    return {"total": len(listar_herramientas()), "por_region": listar_por_region()}


@router.get("/video/ia/conectores")
def api_ia_conectores():
    from ama.video.toolkit.connectors.registry import estado_todos

    return {"conectores": estado_todos()}


@router.get("/director/plan-mes")
def api_director_plan_mes(db: Session = Depends(get_db)):
    from ama.engine.plan_mensual_director import plan_mes_actual

    return plan_mes_actual(db=db)


@router.get("/publish/cola")
def api_publish_cola(estado: str | None = Query(None)):
    from ama.publishers.publish_queue import listar_cola

    return {"items": listar_cola(estado)}


@router.get("/estratega/plan")
def api_estratega_plan(fecha: date | None = Query(None), db: Session = Depends(get_db)):
    return ama_service.estratega_plan_api(fecha, db=db)


@router.post("/publish/aprobar/{pub_id}")
def api_aprobar_publicacion(pub_id: str):
    try:
        return ama_service.aprobar_publicacion_api(pub_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


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
