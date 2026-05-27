"""
Solapamiento de reservas y disponibilidad por noche de calendario.
Una noche d está ocupada si existe reserva con check_in <= d < check_out.
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from backend.models.reserva import ESTADOS_BLOQUEANTES, Reserva
from backend.models.unidad import Unidad


def hay_solape(
    db: Session,
    unidad_id: str,
    check_in: date,
    check_out: date,
    exclude_reserva_id: str | None = None,
) -> bool:
    q = db.query(Reserva.id).filter(
        and_(
            Reserva.unidad_id == unidad_id,
            Reserva.estado.in_(ESTADOS_BLOQUEANTES),
            Reserva.check_in < check_out,
            Reserva.check_out > check_in,
        )
    )
    if exclude_reserva_id:
        q = q.filter(Reserva.id != exclude_reserva_id)
    return q.first() is not None


def estadia_libre(
    db: Session,
    unidad_id: str,
    check_in: date,
    check_out: date,
    exclude_reserva_id: str | None = None,
) -> bool:
    if check_out <= check_in:
        return False
    return not hay_solape(db, unidad_id, check_in, check_out, exclude_reserva_id)


def _unidades_consideradas(db: Session, unidad_id: str | None) -> list[str]:
    if unidad_id:
        u = db.get(Unidad, unidad_id)
        if not u or not u.disponible_para_reserva:
            return []
        return [unidad_id]
    rows = db.query(Unidad).filter(Unidad.activa.is_(True)).order_by(Unidad.numero).all()
    return [x.id for x in rows if x.disponible_para_reserva]


def unidades_ocupadas_en_noche(
    db: Session,
    d: date,
    solo_ids: list[str] | None = None,
) -> set[str]:
    """IDs de unidades con alguna reserva bloqueante que cubre la noche `d`."""
    ids_filter = solo_ids

    base = db.query(Reserva.unidad_id).filter(
        and_(
            Reserva.estado.in_(ESTADOS_BLOQUEANTES),
            Reserva.check_in <= d,
            Reserva.check_out > d,
        )
    )
    if ids_filter:
        base = base.filter(Reserva.unidad_id.in_(ids_filter))
    rows = base.distinct().all()
    return {r[0] for r in rows}


def vista_disponibilidad(
    db: Session,
    desde: date,
    hasta: date,
    unidad_id: str | None = None,
) -> list[dict]:
    """Por cada día en `[desde, hasta]`: unidades disponibles esa noche (si `unidad_id`, solo ese id)."""
    if hasta < desde:
        return []

    ids = _unidades_consideradas(db, unidad_id)
    todas = set(ids)
    resultado: list[dict] = []
    cur = desde
    while cur <= hasta:
        ocupadas = unidades_ocupadas_en_noche(db, cur, solo_ids=ids if ids else None)
        disponibles = sorted(todas - ocupadas)
        if unidad_id:
            resultado.append(
                {"fecha": cur.isoformat(), "disponible": unidad_id in disponibles}
            )
        else:
            resultado.append(
                {"fecha": cur.isoformat(), "disponibles": disponibles}
            )
        cur += timedelta(days=1)
    return resultado
