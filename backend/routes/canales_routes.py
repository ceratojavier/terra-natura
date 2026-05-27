"""Channel manager — sincronización iCal import/export."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services import channel_ical_sync, ical_feeds_service
from backend.services.config_service import get_config

router = APIRouter(prefix="/api/canales", tags=["Channel manager"])


@router.get("/estado")
def estado_canales(db: Session = Depends(get_db)):
    """Resumen feeds iCal y modo solo directo."""
    row = get_config(db, "config_canales") or get_config(db, "canales")
    valor = (row or {}).get("valor") if row else {}
    if not isinstance(valor, dict):
        valor = {}
    norm = ical_feeds_service.normalize_canales(valor)
    check = ical_feeds_service.check_canales(norm)
    return {
        "modo_solo_reserva_directa": bool(norm.get("modo_solo_reserva_directa")),
        "booking_habilitado": norm.get("booking_habilitado", True),
        "airbnb_habilitado": norm.get("airbnb_habilitado", False),
        "feeds_ical": norm.get("feeds_ical", []),
        "resumen": check,
        "export_por_unidad": [
            {"unidad_id": u["id"], "url": f"/api/unidades/{u['id']}/ical"}
            for u in ical_feeds_service.UNIDADES_ICAL
        ],
    }


@router.post("/sync-ical")
def sincronizar_ical(
    dry_run: bool = Query(False, description="Simular sin escribir en BD"),
    db: Session = Depends(get_db),
):
    """
    Descarga calendarios Booking/Airbnb configurados y crea/actualiza reservas bloqueantes.
    La web y el motor de cotización usan la misma ocupación.
    """
    return channel_ical_sync.sync_todos_los_feeds(db, dry_run=dry_run)
