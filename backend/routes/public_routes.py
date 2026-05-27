"""Endpoints públicos para la web de reservas (sin auth staff)."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services import ical_feeds_service, unidad_service
from backend.services.config_service import get_config

router = APIRouter(prefix="/api/public", tags=["Web pública"])

BOOKING_URL_DEFAULT = (
    "https://www.booking.com/hotel/ar/cabanas-alpinas-terra-natura-bialet-masse.es.html"
)
WHATSAPP_RESERVAS = "5493541571190"


@router.get("/motor-reserva")
def config_motor_reserva(db: Session = Depends(get_db)):
    """
    Configuración para el motor JS de la home: unidades, reglas de seña y URLs.
    """
    row = get_config(db, "config_canales") or get_config(db, "canales")
    valor: dict = {}
    if row and isinstance(row.get("valor"), dict):
        valor = row["valor"]

    modo_directo = bool(valor.get("modo_solo_reserva_directa"))
    unidades = unidad_service.list_unidades(db, solo_alquilables=True)

    return {
        "unidades": unidades,
        "reglas": {
            "sena_pct": 50,
            "plazo_senia_horas": 48,
            "moneda": "ARS",
            "check_in_hora": "11:30",
            "check_out_hora": "10:00",
        },
        "canales": {
            "modo_solo_reserva_directa": modo_directo,
            "booking_url": BOOKING_URL_DEFAULT,
            "booking_habilitado": valor.get("booking_habilitado", True) and not modo_directo,
            "whatsapp": WHATSAPP_RESERVAS,
        },
        "api": {
            "cotizar": "/api/cotizar",
            "disponibilidad": "/api/disponibilidad",
            "reservas": "/api/reservas",
            "sync_ical": "/api/canales/sync-ical",
        },
        "ical_unidades": ical_feeds_service.UNIDADES_ICAL,
    }


@router.get("/disponibilidad-resumen")
def disponibilidad_resumen(
    unidad_id: str = Query(...),
    check_in: date = Query(...),
    check_out: date = Query(...),
    db: Session = Depends(get_db),
):
    """Atajo para la web: ¿está libre la estadía completa?"""
    from backend.models.unidad import Unidad
    from backend.services import disponibilidad_service

    if check_out <= check_in:
        raise HTTPException(400, "check_out debe ser posterior a check_in")
    u = db.get(Unidad, unidad_id)
    if not u:
        raise HTTPException(404, "Unidad no encontrada")
    libre = disponibilidad_service.estadia_libre(db, unidad_id, check_in, check_out)
    return {
        "unidad_id": unidad_id,
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "disponible": libre,
    }
