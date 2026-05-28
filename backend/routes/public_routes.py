"""Endpoints públicos para la web de reservas (sin auth staff)."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config import settings
from backend.config.database import get_db
from backend.models.unidad import Unidad
from backend.schemas.reserva import PagarPreferenciaRequest, ReservaCreate
from backend.services import disponibilidad_service, ical_feeds_service, pricing_engine, reserva_service, unidad_service
from backend.services import mercadopago_service
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
            "pagar_preferencia": "/api/public/pagar-preferencia",
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


@router.post("/pagar-preferencia")
def crear_preferencia_pago_web(body: PagarPreferenciaRequest, db: Session = Depends(get_db)):
    """
    Cotiza, crea pre-reserva y devuelve URL de Mercado Pago (seña 50%).
    Usado por la web estática y el motor de reserva.
    """
    u = db.get(Unidad, body.unidad_id)
    if not u or not u.disponible_para_reserva:
        raise HTTPException(404, "Unidad no encontrada")

    if not disponibilidad_service.estadia_libre(db, body.unidad_id, body.check_in, body.check_out):
        raise HTTPException(409, "Fechas no disponibles")

    cot = pricing_engine.cotizar(db, u, body.check_in, body.check_out)
    total = float(cot.total)
    senia = round(total * 0.5)
    try:
        r = reserva_service.crear(
            db,
            ReservaCreate(
                unidad_id=body.unidad_id,
                check_in=body.check_in,
                check_out=body.check_out,
                origen="web_directa",
                huesped_nombre=body.huesped_nombre,
                huesped_email=body.huesped_email,
                personas=body.personas,
                estado="pre_reserva",
            ),
        )
        ref = r.id
    except ValueError as e:
        raise HTTPException(409, str(e)) from e

    site = settings.PUBLIC_SITE_URL or "http://127.0.0.1:8000"
    try:
        pref = mercadopago_service.crear_preferencia_pago(
            titulo=f"{u.nombre} · seña 50%",
            monto_ars=senia,
            email_huesped=body.huesped_email,
            nombre_huesped=body.huesped_nombre,
            external_reference=ref,
            site_url=site,
        )
    except Exception as e:
        raise HTTPException(502, f"No se pudo iniciar Mercado Pago: {e}") from e

    init_point = pref.get("init_point") or pref.get("sandbox_init_point")
    if not init_point:
        raise HTTPException(502, "Mercado Pago no devolvió URL de pago")

    return {
        "preference_id": pref.get("id"),
        "init_point": init_point,
        "reserva_id": ref,
        "total": total,
        "senia": senia,
        "noches": cot.noches,
    }
