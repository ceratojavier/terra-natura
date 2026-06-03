"""
Servicio AMA — expone motor de marketing al API FastAPI.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ama.engine.content_strategist import generar_copy
from ama.storage import calendar_store
from ama.video.slideshow_builder import crear_slideshow


_CANAL_LABEL = {
    "instagram": "Instagram",
    "facebook": "Facebook",
    "whatsapp_status": "WhatsApp Status",
    "tiktok": "TikTok",
}


def _enriquecer_publicacion(p: dict) -> dict:
    canal = p.get("canal") or "instagram"
    return {
        **p,
        "canal_label": _CANAL_LABEL.get(canal, canal.replace("_", " ").title()),
        "tiene_video": bool(p.get("video_ruta")),
    }


def vista_hoy_y_proximas(*, dias_proximos: int = 7) -> dict:
    """Vista operativa diaria: qué publicar hoy y mañana."""
    hoy_d = date.today()
    hoy = hoy_d.isoformat()
    _dias = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo")
    hoy_legible = f"{_dias[hoy_d.weekday()]} {hoy_d.day:02d}/{hoy_d.month:02d}/{hoy_d.year}"
    lim = (hoy_d + timedelta(days=dias_proximos)).isoformat()
    pubs = calendar_store.list_publicaciones()
    hoy_list = sorted(
        [_enriquecer_publicacion(p) for p in pubs if p.get("fecha_publicacion") == hoy],
        key=lambda x: x.get("hora") or "99:99",
    )
    proximas = sorted(
        [
            _enriquecer_publicacion(p)
            for p in pubs
            if p.get("fecha_publicacion") and hoy < p["fecha_publicacion"] <= lim
        ],
        key=lambda x: (x.get("fecha_publicacion") or "", x.get("hora") or ""),
    )[:12]
    pendientes = [p for p in pubs if p.get("estado") in ("borrador", "pendiente_aprobacion")]
    return {
        "fecha_hoy": hoy,
        "fecha_hoy_legible": hoy_legible,
        "publicaciones_hoy": hoy_list,
        "sin_publicaciones_hoy": len(hoy_list) == 0,
        "proximas": proximas,
        "pendientes_aprobacion": len(pendientes),
        "mensaje": (
            "Hoy no hay piezas en Publicaciones. Ejecutá el plan del Director desde la pantalla Hoy."
            if not hoy_list
            else f"{len(hoy_list)} pieza(s) programada(s) para hoy."
        ),
    }


def dashboard() -> dict:
    pubs = calendar_store.list_publicaciones()
    hoy = date.today().isoformat()
    pendientes = [p for p in pubs if p.get("estado") in ("borrador", "pendiente_aprobacion")]
    hoy_list = [p for p in pubs if p.get("fecha_publicacion") == hoy]
    cfg = calendar_store.get_config()
    vh = vista_hoy_y_proximas()
    return {
        "modo_publicacion": cfg.get("modo_publicacion", "aprobacion"),
        "total_calendario": len(pubs),
        "pendientes_aprobacion": len(pendientes),
        "publicaciones_hoy": len(hoy_list),
        "proximas": pubs[:5],
        "hoy_detalle": vh,
        "video_habilitado": cfg.get("video_habilitado", True),
        "publicacion_automatica_redes": False,
        "mensaje": "Modo actual: generás y aprobás; copiás a Instagram/Facebook/WhatsApp. Auto-publicar cuando Meta esté conectado.",
    }


def generar_copy_api(**kwargs) -> dict:
    return generar_copy(**kwargs)


def generar_semana_api(desde: date | None, dias: int, guardar: bool) -> dict:
    from ama.engine.ejecutar_director import mensaje_legacy_deprecado

    return mensaje_legacy_deprecado("POST /api/ama/director/semana/ejecutar")


def generar_calendario_editorial_api(
    *,
    desde: date | None = None,
    hasta: date | None = None,
    dias: int | None = None,
    guardar: bool = True,
    reemplazar_borradores: bool = False,
    db: Any | None = None,
) -> dict:
    from ama.engine.ejecutar_director import mensaje_legacy_deprecado

    _ = (desde, hasta, dias, guardar, reemplazar_borradores, db)
    return mensaje_legacy_deprecado("POST /api/ama/director/semana/ejecutar")


def generar_calendario_90_api(
    desde: date | None,
    dias: int,
    guardar: bool,
    reemplazar_borradores: bool,
    db: Any | None = None,
) -> dict:
    """Compatibilidad: cantidad fija de días desde «desde»."""
    start = desde or date.today()
    return generar_calendario_editorial_api(
        desde=start,
        hasta=start + timedelta(days=dias - 1),
        guardar=guardar,
        reemplazar_borradores=reemplazar_borradores,
        db=db,
    )


def video_slideshow_api(**kwargs) -> dict:
    return crear_slideshow(**kwargs)


def video_desde_guion_api(
    pub_id: str | None = None,
    guion: dict | None = None,
    assets: dict | None = None,
    db: Any | None = None,
) -> dict:
    from ama.storage import calendar_store
    from ama.video.editorial_reel_builder import build_from_guion, build_from_publicacion

    if pub_id:
        pub = calendar_store.get_publicacion(pub_id)
        if not pub:
            return {"ok": False, "mensaje": "Publicación no encontrada"}
        r = build_from_publicacion(pub, db=db)
        if r.get("ok"):
            calendar_store.actualizar_publicacion(pub_id, {"video_ruta": r["ruta"]})
        return r
    if guion:
        return build_from_guion(guion, assets=assets, db=db)
    return {"ok": False, "mensaje": "Indicá pub_id o guion"}


def video_lote_calendario_api(dias: int = 14, max_videos: int = 5, db: Any | None = None) -> dict:
    from ama.video.editorial_reel_builder import build_lote_calendario

    return build_lote_calendario(dias=dias, max_videos=max_videos, db=db)


def pipeline_dia_api(
    fecha: date | None,
    *,
    render_video: bool = True,
    guardar_calendario: bool = True,
    carpeta_media: str | None = "Parque",
    db: Any | None = None,
) -> dict:
    from ama.video.toolkit.pipeline_daily import ejecutar_pipeline_dia

    return ejecutar_pipeline_dia(
        fecha,
        db=db,
        render_video=render_video,
        guardar_calendario=guardar_calendario,
        carpeta_media=carpeta_media,
    )


def estratega_plan_api(fecha: date | None = None, *, db: Any | None = None) -> dict:
    from ama.engine.estratega_dia import planificar_dia

    d = fecha or date.today()
    plan = planificar_dia(d, db=db)
    return {"fecha": d.isoformat(), "plan": plan, "delegado_director": True}


def aprobar_publicacion_api(pub_id: str) -> dict:
    from ama.publishers.publish_queue import actualizar_estado

    row = calendar_store.actualizar_publicacion(pub_id, {"estado": "aprobado"})
    if not row:
        raise ValueError("Publicación no encontrada")
    actualizar_estado(pub_id, "aprobado")
    return row


def cola_publicacion_resumen() -> dict:
    from ama.publishers.publish_queue import listar_cola

    pend = listar_cola("pendiente_aprobacion")
    aprob = listar_cola("aprobado")
    return {
        "pendientes": len(pend),
        "aprobados": len(aprob),
        "items_pendientes": pend[:10],
    }


def pantalla_hoy_api(*, db: Any | None = None) -> dict:
    """Vista dueño: qué mirar hoy (publicación + campaña + acciones claras)."""
    from ama.engine.plan_marketing_unificado import construir_plan_marketing
    from ama.publishers.meta_publisher import estado_conexion_meta

    from ama.engine.director_semanal import planificar_semana
    from ama.engine.scanner_eventos import resumen_para_hoy

    vh = vista_hoy_y_proximas()
    plan = construir_plan_marketing(db=db, dias=120)
    director = planificar_semana(db=db)
    radar = resumen_para_hoy()
    meta = estado_conexion_meta()
    cfg = calendar_store.get_config()

    pendientes = vh.get("pendientes_aprobacion", 0)
    sin_hoy = vh.get("sin_publicaciones_hoy", True)

    if sin_hoy and pendientes == 0 and director.get("total_piezas", 0) > 0:
        frase = (
            f"Esta semana planifiqué {director['total_piezas']} publicación(es). "
            "Tocá «Ejecutar plan del Director» para armar copy y mandarlo a Publicaciones."
        )
        estado = "plan_semanal"
    elif sin_hoy and pendientes == 0:
        frase = "Revisá el plan del Director abajo. Si hay piezas, ejecutalas cuando quieras."
        estado = "plan_semanal"
    elif pendientes > 0:
        frase = f"Tenés {pendientes} publicación(es) para revisar antes de Instagram."
        estado = "revisar"
    elif not sin_hoy:
        frase = vh.get("mensaje", "Hay contenido listo para hoy.")
        estado = "listo"
    else:
        frase = "Todo tranquilo por ahora."
        estado = "ok"

    acciones = [
        {
            "id": "ejecutar_director",
            "titulo": "Ejecutar plan del Director",
            "explicacion": "Armo copy y guion de la semana, encolo en Publicaciones y genero video del reel de hoy si corresponde.",
            "api": "POST /api/ama/director/semana/ejecutar",
        },
        {
            "id": "revisar",
            "titulo": "Ver publicaciones pendientes",
            "explicacion": "Lo que quedó esperando tu OK para subir a redes.",
            "ruta": "/publicaciones",
        },
        {
            "id": "radar",
            "titulo": "Revisar eventos nuevos",
            "explicacion": "Incorporá o descartá novedades antes de que entren al plan.",
            "ruta": "/radar-eventos",
        },
        {
            "id": "plan",
            "titulo": "Ver plan de marketing",
            "explicacion": "Feriados, campañas y calendario anual.",
            "ruta": "/plan",
        },
    ]

    return {
        "estado": estado,
        "frase_principal": frase,
        "fecha_hoy_legible": vh.get("fecha_hoy_legible"),
        "publicaciones_hoy": vh.get("publicaciones_hoy", []),
        "proximas": vh.get("proximas", [])[:5],
        "pendientes_aprobacion": pendientes,
        "campaña_activa": plan.get("campaña_activa"),
        "plan_editorial_hoy": plan.get("plan_editorial_hoy"),
        "director_semanal": director,
        "radar_eventos": radar,
        "instagram": meta,
        "modo_publicacion": cfg.get("modo_publicacion", "aprobacion"),
        "acciones": acciones,
    }


def estrategia_anual_api() -> dict:
    from ama.engine.estrategia_marketing_anual import resumen_plan_anual

    return resumen_plan_anual()


def director_semanal_api(*, ref: date | None = None, db: Any | None = None) -> dict:
    from ama.engine.director_semanal import planificar_semana

    return planificar_semana(ref, db=db)


def director_semanal_producir_api(*, ref: date | None = None, db: Any | None = None) -> dict:
    from ama.engine.director_semanal import desarrollar_semana

    return desarrollar_semana(ref, db=db)


def director_ejecutar_plan_api(
    *,
    ref: date | None = None,
    db: Any | None = None,
    render_video_hoy: bool = True,
    solo_hoy: bool = False,
) -> dict:
    """Produce copy/guion, encola Publicaciones y renderiza reel de hoy si aplica."""
    from ama.engine.ejecutar_director import ejecutar_plan_director

    return ejecutar_plan_director(
        ref,
        db=db,
        render_video_hoy=render_video_hoy,
        enviar_publicaciones=True,
        solo_hoy=solo_hoy,
    )


def scanner_bandeja_api() -> dict:
    from ama.engine.scanner_eventos import listar_bandeja

    return listar_bandeja(solo_pendientes=True)


def scanner_escanear_api(*, db: Any | None = None, actualizar_fuentes: bool = False) -> dict:
    from ama.engine.scanner_eventos import escanear_novedades

    return escanear_novedades(db=db, actualizar_fuentes=actualizar_fuentes)


def scanner_analizar_api(texto: str, *, guardar: bool = False) -> dict:
    from ama.engine.scanner_eventos import analizar_texto_dueño

    return analizar_texto_dueño(texto, guardar=guardar)


def scanner_aviso_api(texto: str) -> dict:
    from ama.engine.scanner_eventos import registrar_aviso

    return registrar_aviso(texto)


def scanner_incorporar_api(item_id: str) -> dict:
    from ama.engine.scanner_eventos import incorporar_evento

    return incorporar_evento(item_id)


def scanner_descartar_api(item_id: str, *, motivo: str = "") -> dict:
    from ama.engine.scanner_eventos import descartar_evento

    return descartar_evento(item_id, motivo=motivo)


def plan_marketing_api(
    *,
    db: Any | None = None,
    anio: int | None = None,
    mes: int | None = None,
    desarrollar_completo: bool = False,
) -> dict:
    from ama.engine.plan_marketing_unificado import construir_plan_marketing

    return construir_plan_marketing(
        db=db,
        dias=365,
        anio=anio,
        mes=mes,
        desarrollar_completo=desarrollar_completo,
    )


def plan_hito_api(hito_id: str, *, db: Any | None = None) -> dict:
    from ama.engine.plan_marketing_unificado import obtener_hito

    h = obtener_hito(hito_id, db=db, desarrollar=True)
    if not h:
        raise ValueError("Campaña no encontrada")
    return h


def plan_pieza_api(hito_id: str, pieza_id: str, *, db: Any | None = None) -> dict:
    from ama.engine.guion_produccion import resolver_pieza_calendario

    p = resolver_pieza_calendario(hito_id, pieza_id, db=db)
    if not p:
        raise ValueError("Publicación del plan no encontrada")
    return p


def guion_produccion_generar_api(hito_id: str, pieza_id: str, *, db: Any | None = None) -> dict:
    from ama.engine.guion_produccion import generar_guion_produccion, resolver_pieza_calendario

    pieza = resolver_pieza_calendario(hito_id, pieza_id, db=db)
    if not pieza:
        raise ValueError("Pieza no encontrada")
    item = {"nombre": pieza.get("hito_nombre"), "tipo": pieza.get("hito_tipo")}
    gp = generar_guion_produccion(pieza, item=item, db=db)
    return {"ok": True, "pieza_id": pieza_id, "hito_id": hito_id, "guion_produccion": gp}


def guion_produccion_escena_api(
    hito_id: str,
    pieza_id: str,
    numero: int,
    *,
    youtube_id: str | None = None,
    youtube_url: str | None = None,
    youtube_inicio_seg: float | None = None,
    youtube_fin_seg: float | None = None,
    foto_ruta: str | None = None,
) -> dict:
    from ama.engine.guion_produccion import generar_guion_produccion, resolver_pieza_calendario
    from ama.engine.guion_produccion_store import actualizar_escena
    from ama.video.youtube_broll import parse_youtube_id

    yid = youtube_id
    if not yid and youtube_url:
        yid = parse_youtube_id(youtube_url)
    actualizar_escena(
        pieza_id,
        numero,
        youtube_id=yid,
        youtube_url=youtube_url,
        youtube_inicio_seg=youtube_inicio_seg,
        youtube_fin_seg=youtube_fin_seg,
        foto_ruta=foto_ruta,
    )
    pieza = resolver_pieza_calendario(hito_id, pieza_id, db=db)
    if not pieza:
        raise ValueError("Pieza no encontrada")
    gp = generar_guion_produccion(pieza, db=db)
    return {"ok": True, "guion_produccion": gp}


def guion_produccion_render_api(hito_id: str, pieza_id: str, *, db: Any | None = None) -> dict:
    from ama.engine.guion_produccion import render_video_produccion

    return render_video_produccion(hito_id, pieza_id, db=db)


def pieza_enviar_publicaciones_api(
    hito_id: str,
    pieza_id: str,
    *,
    video_ruta: str | None = None,
    db: Any | None = None,
) -> dict:
    """Crea fila en cola Publicaciones desde pieza del calendario/plan."""
    from pathlib import Path

    from ama.engine.guion_produccion import resolver_pieza_calendario
    from ama.storage import calendar_store

    pieza = resolver_pieza_calendario(hito_id, pieza_id, db=db)
    if not pieza:
        raise ValueError("Pieza no encontrada")

    fp = pieza.get("fecha_publicacion")
    if not fp:
        raise ValueError("La pieza no tiene fecha de publicación")

    ruta_video = video_ruta
    if not ruta_video:
        repo = Path(__file__).resolve().parent.parent.parent
        out_dir = repo / "ama" / "output" / "video"
        if out_dir.is_dir():
            slug = pieza_id.replace("|", "_").replace("/", "_")[:48]
            candidatos = sorted(
                out_dir.glob(f"*{slug}*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if candidatos:
                ruta_video = str(candidatos[0].relative_to(repo)).replace("\\", "/")

    cfg = calendar_store.get_config()
    estado = (
        "pendiente_aprobacion"
        if cfg.get("modo_publicacion", "aprobacion") == "aprobacion"
        else "borrador"
    )

    copy = (pieza.get("copy_instagram") or pieza.get("copy") or "").strip()
    if not copy and pieza.get("guion"):
        g = pieza["guion"]
        hook = g.get("hook") or ""
        voz = g.get("voz_off") or ""
        copy = f"{hook}\n\n{voz}".strip()

    row = calendar_store.crear_publicacion(
        {
            "fecha_publicacion": fp,
            "hora": pieza.get("hora_publicacion", "10:00"),
            "canal": pieza.get("canal", "instagram"),
            "angulo": pieza.get("angulo", "parejas"),
            "titulo": pieza.get("titulo_publicacion", ""),
            "copy": copy,
            "hashtags": pieza.get("hashtags") or [],
            "estado": estado,
            "formato": pieza.get("formato", "reel"),
            "guion": pieza.get("guion_json") or pieza.get("guion"),
            "video_ruta": ruta_video,
            "notas": f"pieza:{hito_id}/{pieza_id}",
            "objetivo": pieza.get("objetivo", "cta_reserva"),
        }
    )
    return {
        "ok": True,
        "publicacion": row,
        "mensaje": "Listo en Publicaciones — revisá copy y video antes de aprobar.",
    }


def calendario_visual_api(
    *,
    anio: int | None = None,
    mes: int | None = None,
    db: Any | None = None,
) -> dict:
    from datetime import date as _date
    from ama.engine.calendario_visual import construir_calendario_visual_mes

    hoy = _date.today()
    anio = anio or hoy.year
    mes = mes or hoy.month
    return construir_calendario_visual_mes(anio=anio, mes=mes, db=db)


def preparar_contenido_hoy_api(*, db: Any | None = None) -> dict:
    """Legacy — redirige al Director Semanal (solo piezas de hoy)."""
    return director_ejecutar_plan_api(db=db, render_video_hoy=True, solo_hoy=True)


def publicar_en_instagram_api(pub_id: str) -> dict:
    from ama.publishers.meta_publisher import publicar_publicacion
    from ama.publishers.publish_queue import actualizar_estado

    pubs = calendar_store.list_publicaciones()
    row = next((p for p in pubs if p.get("id") == pub_id), None)
    if not row:
        raise ValueError("Publicación no encontrada")

    res = publicar_publicacion(row)
    if res.get("ok"):
        calendar_store.actualizar_publicacion(pub_id, {"estado": "publicado"})
        actualizar_estado(pub_id, "publicado", plataforma_respuesta=res)
    return res
