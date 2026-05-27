"""
Servicio AMA — expone motor de marketing al API FastAPI.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ama.engine.content_strategist import generar_copy
from ama.engine.season_planner import aplicar_sugerencias_a_calendario, sugerir_semana
from ama.storage import calendar_store
from ama.video.slideshow_builder import crear_slideshow


def dashboard() -> dict:
    pubs = calendar_store.list_publicaciones()
    hoy = date.today().isoformat()
    pendientes = [p for p in pubs if p.get("estado") in ("borrador", "pendiente_aprobacion")]
    hoy_list = [p for p in pubs if p.get("fecha_publicacion") == hoy]
    cfg = calendar_store.get_config()
    return {
        "modo_publicacion": cfg.get("modo_publicacion", "aprobacion"),
        "total_calendario": len(pubs),
        "pendientes_aprobacion": len(pendientes),
        "publicaciones_hoy": len(hoy_list),
        "proximas": pubs[:5],
        "video_habilitado": cfg.get("video_habilitado", True),
        "publicacion_automatica_redes": False,
        "mensaje": "Modo actual: generás y aprobás; copiás a Instagram/Facebook/WhatsApp. Auto-publicar cuando Meta esté conectado.",
    }


def generar_copy_api(**kwargs) -> dict:
    return generar_copy(**kwargs)


def generar_semana_api(desde: date | None, dias: int, guardar: bool) -> dict:
    if guardar:
        creadas = aplicar_sugerencias_a_calendario(desde, dias)
        return {"guardadas": len(creadas), "items": creadas}
    return {"guardadas": 0, "items": sugerir_semana(desde, dias)}


def _rango_hasta_marzo(inicio: date) -> date:
    anio_marzo = inicio.year + 1 if inicio.month > 3 else inicio.year
    return date(anio_marzo, 3, 31)


def generar_calendario_editorial_api(
    *,
    desde: date | None = None,
    hasta: date | None = None,
    dias: int | None = None,
    guardar: bool = True,
    reemplazar_borradores: bool = False,
    db: Any | None = None,
) -> dict:
    from ama.engine.calendar_90_planner import (
        aplicar_a_calendario,
        exportar_preview,
        planificar_rango,
        resumen_plan,
    )

    start = desde or date.today()
    end = hasta or (start + timedelta(days=(dias or 90) - 1))
    if end < start:
        end = start
    max_dias = 366
    if (end - start).days + 1 > max_dias:
        end = start + timedelta(days=max_dias - 1)

    items = planificar_rango(desde=start, hasta=end, db=db)
    resumen = resumen_plan(items)
    export_path = exportar_preview(items)
    dias_total = (end - start).days + 1
    out = {
        "ok": True,
        "desde": start.isoformat(),
        "hasta": end.isoformat(),
        "dias": dias_total,
        "resumen": resumen,
        "export_json": str(export_path.name),
        "items_muestra": items[:5],
    }
    if guardar:
        creadas = aplicar_a_calendario(
            items,
            reemplazar_borrador_en_rango=reemplazar_borradores,
            desde=start,
            hasta=end,
        )
        out["guardadas"] = len(creadas)
    else:
        out["guardadas"] = 0
        out["items"] = items
    return out


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
