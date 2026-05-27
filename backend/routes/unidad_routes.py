from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.config.settings import ICAL_FEED_TOKEN, USOS_UNIDAD
from backend.schemas.unidad import UnidadUpdate
from backend.services import ical_export_service, unidad_service

router = APIRouter(prefix="/api/unidades", tags=["Unidades"])


@router.get("/{unidad_id}/ical", include_in_schema=True)
def exportar_ics_ocupacion(
    unidad_id: str,
    token: str | None = Query(None, description="Obligatorio si ICAL_FEED_TOKEN está configurado"),
    db: Session = Depends(get_db),
):
    """
    Feed de bloqueos para importar en Booking/Airbnb (URL pública opcional).
    Si definís `ICAL_FEED_TOKEN` en `.env`, el query `?token=` debe coincidir.
    """
    if ICAL_FEED_TOKEN and token != ICAL_FEED_TOKEN:
        raise HTTPException(401, "Token inválido o ausente")

    u = unidad_service.get_unidad(db, unidad_id)
    if not u:
        raise HTTPException(404, "Unidad no encontrada")

    body = ical_export_service.generar_ics_ocupacion(
        db, unidad_id, nombre_unidad=u["nombre"]
    )
    return Response(
        content=body.encode("utf-8"),
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'inline; filename="{unidad_id}.ics"',
        },
    )


@router.get("")
def listar_unidades(
    solo_alquilables: bool = Query(False, description="Solo unidades en modo alquiler activo"),
    db: Session = Depends(get_db),
):
    return {
        "total": unidad_service.contar_unidades_reservables(db) if solo_alquilables else None,
        "unidades": unidad_service.list_unidades(db, solo_alquilables=solo_alquilables),
        "usos_modo_posibles": list(USOS_UNIDAD),
    }


@router.get("/{unidad_id}")
def obtener_unidad(unidad_id: str, db: Session = Depends(get_db)):
    u = unidad_service.get_unidad(db, unidad_id)
    if not u:
        raise HTTPException(404, "Unidad no encontrada")
    return u


@router.patch("/{unidad_id}")
def actualizar_unidad(
    unidad_id: str,
    body: UnidadUpdate,
    db: Session = Depends(get_db),
):
    try:
        data = body.model_dump(exclude_unset=True)
        u = unidad_service.update_unidad(db, unidad_id, data)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    if not u:
        raise HTTPException(404, "Unidad no encontrada")
    return u
