"""
WhatsApp Cloud API — envío y parseo de webhooks Meta.
"""
from __future__ import annotations

import logging
import re
from typing import Any

import httpx

from backend.config.settings import (
    WHATSAPP_CLOUD_TOKEN,
    WHATSAPP_OWNER_PHONE,
    WHATSAPP_PHONE_NUMBER_ID,
)

logger = logging.getLogger(__name__)

_GRAPH = "https://graph.facebook.com/v21.0"


def whatsapp_configurado() -> bool:
    return bool(WHATSAPP_CLOUD_TOKEN and WHATSAPP_PHONE_NUMBER_ID)


def _normalizar_telefono(numero: str) -> str:
    return re.sub(r"\D", "", (numero or "").strip())


def enviar_texto(to: str, body: str) -> dict[str, Any]:
    """Envía mensaje de texto. `to` = número internacional sin +."""
    if not whatsapp_configurado():
        return {"ok": False, "error": "whatsapp_no_configurado"}
    dest = _normalizar_telefono(to)
    if not dest or not (body or "").strip():
        return {"ok": False, "error": "destino_o_texto_vacio"}

    url = f"{_GRAPH}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": dest,
        "type": "text",
        "text": {"preview_url": False, "body": body.strip()[:4096]},
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {WHATSAPP_CLOUD_TOKEN}"},
            )
            r.raise_for_status()
            data = r.json()
            return {"ok": True, "message_id": (data.get("messages") or [{}])[0].get("id")}
    except Exception as e:
        logger.warning("whatsapp enviar_texto: %s", e)
        return {"ok": False, "error": str(e)}


def notificar_dueno(texto: str) -> dict[str, Any]:
    """Aviso al dueño (mismo número comercial por defecto)."""
    return enviar_texto(WHATSAPP_OWNER_PHONE, texto)


def extraer_mensajes_entrantes(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Devuelve [{from, text, message_id}] de un webhook Meta."""
    out: list[dict[str, str]] = []
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            for msg in value.get("messages") or []:
                if msg.get("type") != "text":
                    continue
                text = (msg.get("text") or {}).get("body") or ""
                sender = str(msg.get("from") or "")
                mid = str(msg.get("id") or "")
                if sender and text.strip():
                    out.append({"from": sender, "text": text.strip(), "message_id": mid})
    return out
