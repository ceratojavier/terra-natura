"""
Planificador calendario editorial por rango de fechas — CTA, fidelización, utilidad, branding.
(Compat: planificar_90_dias = atajo por cantidad de días.)
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from ama.engine.calendar_context import evento_en_fecha, reglas_editoriales
from ama.engine.content_strategist import generar_copy
from ama.engine.media_picker import armar_assets
from ama.engine.script_generator import generar_guion

_EXPORT = Path(__file__).resolve().parent.parent / "data" / "calendario_90_ultimo.json"


def _angulo_desde_objetivo(objetivo: str, evento: dict | None) -> str:
    if evento:
        if evento.get("tipo") == "finde_largo":
            return evento.get("angulo_campana", "evento")
        if evento.get("tipo") == "vacaciones_invierno":
            return "familia"
        if evento.get("tipo") == "feriado":
            return "evento"
    m = {
        "cta_reserva": "reserva_directa",
        "fidelizacion": "parejas",
        "utilidad": "familia",
        "branding": "parejas",
    }
    return m.get(objetivo, "parejas")


def _objetivo_ajustado(base: str, evento: dict | None) -> str:
    if evento and evento.get("tipo") in ("finde_largo", "feriado"):
        return "cta_reserva"
    if evento and evento.get("tipo") == "vacaciones_invierno" and base == "branding":
        return "cta_reserva"
    return base


def _cuerpo_extra(objetivo: str, evento: dict | None, d: date) -> str | None:
    if evento:
        if evento.get("copy_hook"):
            return evento["copy_hook"]
        if evento.get("mensaje_campana"):
            return evento["mensaje_campana"]
        if evento.get("nombre"):
            return f"{evento['nombre']} — consultá fechas libres en Bialet Massé."
    if objetivo == "fidelizacion":
        return "Quienes ya nos visitaron saben: tranquilidad, pileta y dueños en el predio. ¿Volvemos a verte?"
    if objetivo == "utilidad":
        if d.month in (1, 2):
            return "Verano: llevar protector solar, reservar asador con anticipación y consultar horario pileta."
        if d.month in (6, 7, 8):
            return "Invierno en Punilla: abrigo para la noche, fogón supervisado y Alpinas con calefacción en PA."
        return "Tip: combiná 2 noches en Alpina + paseo al Labios del Indio o Barrancas Bermejas."
    if objetivo == "branding":
        return "Un refugio en el Valle de Punilla — diseñado para parejas, flexible para familias con menores."
    return None


def planificar_rango(
    *,
    desde: date,
    hasta: date,
    db: Any | None = None,
) -> list[dict]:
    """Genera publicaciones para cada día del rango [desde, hasta] (7 piezas/semana según reglas)."""
    dias = max(1, (hasta - desde).days + 1)
    return planificar_90_dias(desde=desde, dias=dias, db=db)


def planificar_90_dias(
    *,
    desde: date | None = None,
    dias: int = 90,
    db: Any | None = None,
) -> list[dict]:
    """Genera lista de publicaciones planificadas (no guardadas)."""
    reglas = reglas_editoriales()
    rotacion = reglas.get("rotacion_semanal") or []
    horarios = reglas.get("horarios_sugeridos") or {}
    carpetas = reglas.get("carpetas_media_por_angulo") or {}
    start = desde or date.today()
    n_semanas = (dias + 6) // 7
    items: list[dict] = []

    for sem in range(n_semanas):
        for slot in rotacion:
            d = start + timedelta(days=sem * 7 + slot["dia"])
            if (d - start).days >= dias:
                break
            ev = evento_en_fecha(d)
            objetivo = _objetivo_ajustado(slot.get("objetivo_base", "branding"), ev)
            angulo = _angulo_desde_objetivo(objetivo, ev)
            canal = slot["canal"]
            formato = slot.get("formato", "post")
            hora = horarios.get(canal, "10:00")
            tema = "feriado_puente" if ev and ev.get("tipo") == "finde_largo" else ""
            if d.month in (1, 2) and objetivo == "cta_reserva":
                tema = "verano"
            if objetivo == "cta_reserva" and d.month in (6, 7, 8):
                tema = "promo_baja"

            cuerpo = _cuerpo_extra(objetivo, ev, d)
            canal_copy = canal if canal in ("instagram", "facebook", "whatsapp_status", "tiktok") else "instagram"
            gen = generar_copy(
                angulo=angulo,
                canal=canal_copy,
                tema_extra=tema,
                cuerpo_extra=cuerpo,
            )

            carpeta = carpetas.get(angulo) or carpetas.get("utilidad")
            assets = armar_assets(
                carpeta_media=carpeta,
                db=db,
                tema_youtube=ev.get("nombre", "Bialet") if ev else "Valle de Punilla",
                incluir_video=True,
            )
            guion = generar_guion(
                objetivo=objetivo,
                canal=canal,
                formato=formato,
                angulo=angulo,
                titulo=gen["titulo"],
                evento=ev,
                assets=assets,
            )

            motivo = f"{objetivo} · {formato}"
            if ev:
                motivo += f" · {ev.get('nombre', ev.get('tipo', ''))}"

            items.append(
                {
                    "fecha_publicacion": d.isoformat(),
                    "hora": hora,
                    "canal": canal,
                    "formato": formato,
                    "objetivo": objetivo,
                    "angulo": angulo,
                    "titulo": gen["titulo"],
                    "copy": gen["copy"],
                    "hashtags": gen["hashtags"],
                    "whatsapp_url": gen.get("whatsapp_url"),
                    "brief_canva": gen.get("brief_canva"),
                    "guion": guion,
                    "assets": assets,
                    "estado_sugerido": "borrador",
                    "motivo": motivo,
                    "evento_calendario": ev,
                }
            )

    return items


def _adaptar_tiktok(copy: str, objetivo: str) -> str:
    lines = [ln.strip() for ln in copy.split("\n") if ln.strip()]
    short = lines[:4]
    if objetivo == "cta_reserva":
        short.append("Reservá por WhatsApp — link en bio")
    return "\n".join(short)


def aplicar_a_calendario(
    items: list[dict],
    *,
    reemplazar_borrador_en_rango: bool = False,
    desde: date | None = None,
    dias: int = 90,
    hasta: date | None = None,
) -> list[dict]:
    from ama.storage.calendar_store import crear_publicacion, list_publicaciones, eliminar_publicacion

    if reemplazar_borrador_en_rango and desde:
        fin = hasta or (desde + timedelta(days=dias))
        for p in list_publicaciones(desde=desde, hasta=fin, estado="borrador"):
            if p.get("id"):
                eliminar_publicacion(p["id"])

    creadas = []
    for s in items:
        row = crear_publicacion(
            {
                "fecha_publicacion": s["fecha_publicacion"],
                "hora": s["hora"],
                "canal": s["canal"],
                "angulo": s["angulo"],
                "titulo": s["titulo"],
                "copy": s["copy"],
                "hashtags": s["hashtags"],
                "estado": "borrador",
                "notas": s.get("motivo", ""),
                "objetivo": s.get("objetivo"),
                "formato": s.get("formato"),
                "guion": s.get("guion"),
                "assets": s.get("assets"),
                "brief_canva": s.get("brief_canva"),
                "whatsapp_url": s.get("whatsapp_url"),
            }
        )
        creadas.append(row)
    return creadas


def exportar_preview(items: list[dict]) -> Path:
    _EXPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generado": date.today().isoformat(),
        "total": len(items),
        "publicaciones": items,
    }
    with _EXPORT.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return _EXPORT


def resumen_plan(items: list[dict]) -> dict:
    por_canal: dict[str, int] = {}
    por_obj: dict[str, int] = {}
    for it in items:
        por_canal[it["canal"]] = por_canal.get(it["canal"], 0) + 1
        por_obj[it.get("objetivo", "?")] = por_obj.get(it.get("objetivo", "?"), 0) + 1
    return {
        "total": len(items),
        "por_canal": por_canal,
        "por_objetivo": por_obj,
        "con_guion": sum(1 for i in items if i.get("guion")),
        "con_fotos": sum(1 for i in items if (i.get("assets") or {}).get("fotos")),
    }
