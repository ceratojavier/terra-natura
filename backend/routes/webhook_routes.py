"""
Webhooks externos (WhatsApp Cloud API, etc.).
"""
import logging
from typing import Any

from fastapi import APIRouter, Body, Request
from fastapi.responses import PlainTextResponse

from backend.config.settings import INSTAGRAM_VERIFY_TOKEN, WHATSAPP_VERIFY_TOKEN

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@router.get("/whatsapp")
async def whatsapp_verify(request: Request):
    """
    Meta envía GET con hub.mode, hub.verify_token, hub.challenge al suscribir el webhook.
    """
    q = request.query_params
    mode = q.get("hub.mode")
    token = q.get("hub.verify_token")
    challenge = q.get("hub.challenge")
    if mode == "subscribe" and challenge:
        if WHATSAPP_VERIFY_TOKEN and token == WHATSAPP_VERIFY_TOKEN:
            return PlainTextResponse(challenge)
        if not WHATSAPP_VERIFY_TOKEN:
            logger.warning(
                "WHATSAPP_VERIFY_TOKEN vacío: Meta no va a poder verificar el webhook."
            )
            return PlainTextResponse("configura WHATSAPP_VERIFY_TOKEN en .env", status_code=503)
        return PlainTextResponse("token inválido", status_code=403)
    return {"info": "Webhook WhatsApp: verificación (GET) y mensajes (POST)."}


@router.post("/whatsapp")
async def whatsapp_entrante(payload: dict[str, Any] = Body(default_factory=dict)):
    """Mensajes entrantes de Meta. Siguiente: parser + ama.chat.responder + PMS."""
    logger.info("webhook whatsapp: %s", list(payload.keys())[:25])
    return {"recibido": True, "nota": "Próximo: cotizar con el mismo motor que la web."}


@router.get("/instagram")
async def instagram_verify(request: Request):
    """
    Meta envía GET con hub.mode, hub.verify_token, hub.challenge para Instagram.
    """
    q = request.query_params
    mode = q.get("hub.mode")
    token = q.get("hub.verify_token")
    challenge = q.get("hub.challenge")
    if mode == "subscribe" and challenge:
        if INSTAGRAM_VERIFY_TOKEN and token == INSTAGRAM_VERIFY_TOKEN:
            return PlainTextResponse(challenge)
        if not INSTAGRAM_VERIFY_TOKEN:
            logger.warning(
                "INSTAGRAM_VERIFY_TOKEN vacío: Meta no va a poder verificar el webhook."
            )
            return PlainTextResponse(
                "configura INSTAGRAM_VERIFY_TOKEN en .env", status_code=503
            )
        return PlainTextResponse("token inválido", status_code=403)
    return {"info": "Webhook Instagram: verificación (GET) y eventos (POST)."}


@router.post("/instagram")
async def instagram_entrante(payload: dict[str, Any] = Body(default_factory=dict)):
    """Eventos entrantes de Instagram Graph Webhooks (comentarios, menciones, etc.)."""
    logger.info("webhook instagram: %s", list(payload.keys())[:25])
    return {"recibido": True, "nota": "Pendiente: procesar eventos de IG."}
