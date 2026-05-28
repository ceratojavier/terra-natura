"""Preferencias de pago Mercado Pago — reserva directa web."""
from __future__ import annotations

import uuid
from datetime import date

import httpx

from backend.config import settings

MP_PREFERENCES_URL = "https://api.mercadopago.com/checkout/preferences"


def crear_preferencia_pago(
    *,
    titulo: str,
    monto_ars: float,
    email_huesped: str,
    nombre_huesped: str,
    external_reference: str,
    site_url: str,
) -> dict:
    token = settings.MERCADOPAGO_ACCESS_TOKEN
    if not token:
        raise ValueError("MERCADOPAGO_ACCESS_TOKEN no configurado en el servidor")

    base = site_url.rstrip("/")
    payload = {
        "items": [
            {
                "id": external_reference[:40],
                "title": titulo[:256],
                "quantity": 1,
                "unit_price": float(monto_ars),
                "currency_id": "ARS",
            }
        ],
        "payer": {"name": nombre_huesped[:100], "email": email_huesped},
        "external_reference": external_reference,
        "back_urls": {
            "success": f"{base}/reserva-exito.html",
            "failure": f"{base}/reserva-fallo.html",
            "pending": f"{base}/reserva-pendiente.html",
        },
        "auto_return": "approved",
        "notification_url": f"{base}/api/webhooks/mercadopago",
    }

    with httpx.Client(timeout=30.0) as client:
        res = client.post(
            MP_PREFERENCES_URL,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
        )
        res.raise_for_status()
        return res.json()


def nueva_referencia() -> str:
    return str(uuid.uuid4())
