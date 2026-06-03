from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.unidad import Unidad
from backend.schemas.reserva import (
    CotizarRequest,
    ReservaCreate,
    ReservaOperacionCreate,
    ReservaOperacionOut,
    ReservaOut,
    ReservaPatch,
)
from backend.services import disponibilidad_service, pricing_engine, reserva_service

router = APIRouter(tags=["Reservas y cotización"], prefix="/api")


@router.post("/cotizar")
def cotizar(payload: CotizarRequest, db: Session = Depends(get_db)):
    u = db.get(Unidad, payload.unidad_id)
    if not u:
        raise HTTPException(404, "Unidad no encontrada")
    if not u.disponible_para_reserva:
        raise HTTPException(400, "Unidad no reservable")

    disponible = disponibilidad_service.estadia_libre(
        db,
        payload.unidad_id,
        payload.check_in,
        payload.check_out,
    )

    cot = pricing_engine.cotizar(
        db,
        u,
        payload.check_in,
        payload.check_out,
        promo=payload.promo,
        aplicar_precio_efectivo=payload.aplicar_precio_efectivo,
    )
    return {
        "disponible": disponible,
        "cotizacion": cot.model_dump(mode="json"),
    }


@router.get("/disponibilidad")
def disponibilidad(
    desde: date = Query(..., description="Primera fecha (solo fecha, sin TZ)"),
    hasta: date = Query(...),
    unidad_id: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Por día: lista `disponibles` o si filtrás `unidad_id`, campo `disponible` bool."""
    if hasta < desde:
        raise HTTPException(400, "hasta debe ser >= desde")
    if unidad_id and not db.get(Unidad, unidad_id):
        raise HTTPException(404, "Unidad no encontrada")
    dias = disponibilidad_service.vista_disponibilidad(db, desde, hasta, unidad_id)
    return {"desde": desde.isoformat(), "hasta": hasta.isoformat(), "dias": dias}


@router.post("/reservas/operacion", response_model=ReservaOperacionOut)
def crear_reserva_operacion(body: ReservaOperacionCreate, db: Session = Depends(get_db)):
    """Alta manual confirmada — panel móvil / operación del complejo."""
    try:
        r, codigo, mensaje = reserva_service.crear_operacion(db, body)
    except ValueError as e:
        raise HTTPException(409 if "solape" in str(e).lower() else 400, str(e)) from e
    out = reserva_service.obtener(db, r.id)
    if not out:
        raise HTTPException(500, "Reserva creada pero no recuperable")
    return ReservaOperacionOut(**out, codigo_reserva=codigo, mensaje_huesped=mensaje)


@router.post("/reservas", response_model=ReservaOut)
def crear_reserva(body: ReservaCreate, db: Session = Depends(get_db)):
    try:
        r = reserva_service.crear(db, body)
    except ValueError as e:
        raise HTTPException(409 if "solape" in str(e).lower() else 400, str(e)) from e
    out = reserva_service.obtener(db, r.id)
    if not out:
        raise HTTPException(500, "Reserva creada pero no recuperable")
    return ReservaOut(**out)


@router.patch("/reservas/{reserva_id}", response_model=ReservaOut)
def actualizar_reserva(reserva_id: str, body: ReservaPatch, db: Session = Depends(get_db)):
    try:
        r = reserva_service.patch(db, reserva_id, body)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    if not r:
        raise HTTPException(404, "Reserva no encontrada")
    out = reserva_service.obtener(db, r.id)
    if not out:
        raise HTTPException(404, "Reserva no encontrada")
    return ReservaOut(**out)


@router.get("/reservas", response_model=list[ReservaOut])
def listar_reservas(
    unidad_id: str | None = None,
    desde: date | None = Query(None),
    hasta: date | None = Query(None),
    db: Session = Depends(get_db),
):
    if (desde is None) != (hasta is None):
        raise HTTPException(400, "Enviá ambos desde y hasta o ninguno")
    rows = reserva_service.listar(db, unidad_id=unidad_id, desde=desde, hasta=hasta)
    return [ReservaOut(**x) for x in rows]


@router.get("/reservas/{reserva_id}", response_model=ReservaOut)
def obtener_reserva(reserva_id: str, db: Session = Depends(get_db)):
    row = reserva_service.obtener(db, reserva_id)
    if not row:
        raise HTTPException(404, "Reserva no encontrada")
    return ReservaOut(**row)
