"""
Procesamiento de mensajes WhatsApp entrantes — cotización + respuesta automática.
"""
from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from ama.chat.responder import responder_consulta_texto_plano
from backend.models.unidad import Unidad
from backend.services import disponibilidad_service, pricing_engine, unidad_service, whatsapp_cloud_service

logger = logging.getLogger(__name__)

_DATE_PATTERNS = (
    re.compile(r"(\d{1,2})[/.-](\d{1,2})(?:[/.-](\d{2,4}))?"),
    re.compile(r"(\d{1,2})\s+al\s+(\d{1,2})"),
)


def _parse_fecha(partes: tuple, ref: date) -> date | None:
    try:
        d = int(partes[0])
        m = int(partes[1])
        y = int(partes[2]) if len(partes) > 2 and partes[2] else ref.year
        if y < 100:
            y += 2000
        return date(y, m, d)
    except (ValueError, TypeError):
        return None


def _extraer_fechas(texto: str, ref: date | None = None) -> tuple[date | None, date | None]:
    """Intento liviano DD/MM o DD/MM/YYYY — dos fechas = estadía."""
    ref = ref or date.today()
    t = (texto or "").lower()
    fechas: list[date] = []
    for pat in _DATE_PATTERNS:
        for m in pat.finditer(t):
            g = m.groups()
            if len(g) >= 2:
                fd = _parse_fecha((g[0], g[1], g[2] if len(g) > 2 else None), ref)
                if fd and fd not in fechas:
                    fechas.append(fd)
    if len(fechas) >= 2:
        fechas.sort()
        return fechas[0], fechas[1]
    if len(fechas) == 1:
        return fechas[0], fechas[0] + timedelta(days=2)
    return None, None


def _unidad_sugerida(texto: str) -> str:
    t = (texto or "").lower()
    if "suite" in t or "loft" in t:
        if "5" in t:
            return "suite-5"
        if "4" in t:
            return "suite-4"
        return "suite-4"
    if "alpina" in t or "caba" in t:
        for n in ("1", "2", "3"):
            if n in t:
                return f"alpina-{n}"
        return "alpina-1"
    return "alpina-1"


def procesar_mensaje_cliente(db: Session, texto: str, *, telefono: str = "") -> str:
    """
    Respuesta para el huésped: reglas AMA + cotización real si hay fechas.
    """
    borrador = responder_consulta_texto_plano(texto)
    ci, co = _extraer_fechas(texto)
    unidad_id = _unidad_sugerida(texto)

    if ci and co and co > ci:
        try:
            if disponibilidad_service.estadia_libre(db, unidad_id, ci, co):
                u_obj = db.get(Unidad, unidad_id)
                if not u_obj:
                    raise ValueError("unidad")
                cot = pricing_engine.cotizar(db, u_obj, ci, co)
                total = float(cot.total or 0)
                noches = int(cot.noches or (co - ci).days)
                u = unidad_service.get_unidad(db, unidad_id) or {}
                nombre_u = u.get("nombre") or unidad_id
                total_fmt = f"${int(total):,}".replace(",", ".") if total else "consultar"
                return (
                    f"Hola 😊 Revisé el calendario del complejo.\n\n"
                    f"*{nombre_u}* — del {ci.strftime('%d/%m/%Y')} al {co.strftime('%d/%m/%Y')} "
                    f"({noches} noche{'s' if noches != 1 else ''})\n"
                    f"Total orientativo: *{total_fmt}* (ARS, reserva directa).\n\n"
                    f"Si te cierra, te confirmamos por acá con seña 50 %.\n"
                    f"¿Cuántas personas serían?"
                )
            u = unidad_service.get_unidad(db, unidad_id) or {}
            return (
                f"Hola 😊 Para esas fechas *{u.get('nombre', unidad_id)}* no tenemos lugar.\n"
                f"Pasame otras fechas o si aceptan otra unidad (Alpina o Suite) y lo revisamos."
            )
        except Exception as e:
            logger.warning("whatsapp cotizar: %s", e)

    return borrador.texto


def procesar_webhook(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    """Parsea webhook Meta, responde a clientes y devuelve resumen."""
    mensajes = whatsapp_cloud_service.extraer_mensajes_entrantes(payload)
    if not mensajes:
        return {"procesados": 0, "nota": "sin mensajes de texto"}

    resultados = []
    for msg in mensajes:
        texto = msg["text"]
        sender = msg["from"]
        respuesta = procesar_mensaje_cliente(db, texto, telefono=sender)
        envio = whatsapp_cloud_service.enviar_texto(sender, respuesta)
        resultados.append(
            {
                "from": sender,
                "respondido": bool(envio.get("ok")),
                "escalado": False,
            }
        )
    return {"procesados": len(resultados), "detalle": resultados}
