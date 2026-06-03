"""
Alta y listado de reservas contra disponibilidad y pricing_engine.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from backend.models.reserva import Reserva
from backend.models.unidad import Unidad
from backend.schemas.reserva import ReservaCreate, ReservaOperacionCreate, ReservaPatch
from backend.services import disponibilidad_service, pricing_engine


def _to_out(r: Reserva) -> dict:
    return {
        "id": r.id,
        "unidad_id": r.unidad_id,
        "check_in": r.check_in,
        "check_out": r.check_out,
        "estado": r.estado,
        "origen": r.origen,
        "huesped_nombre": r.huesped_nombre,
        "personas": r.personas,
        "precio_total": float(r.precio_total),
        "moneda": r.moneda,
    }


ESTADOS_ALTA_ABIERTOS = frozenset({"pre_reserva", "pendiente_pago"})


def codigo_reserva_amigable(reserva_id: str) -> str:
    compact = reserva_id.replace("-", "")[:8].upper()
    return f"TN-{compact}"


def _mensaje_confirmacion_huesped(
    *,
    codigo: str,
    huesped: str,
    unidad_nombre: str,
    check_in: date,
    check_out: date,
    total: float,
) -> str:
    total_txt = f"${int(round(total)):,}".replace(",", ".")
    return (
        f"Hola {huesped}, tu reserva en Terra Natura quedó confirmada.\n"
        f"Código: {codigo}\n"
        f"{unidad_nombre} · entrada {check_in.strftime('%d/%m/%Y')} · "
        f"salida {check_out.strftime('%d/%m/%Y')}\n"
        f"Total acordado: {total_txt}\n"
        f"Los Talas 759, Bialet Massé. Cualquier duda, escribinos por acá."
    )


def crear(db: Session, body: ReservaCreate) -> Reserva:
    if body.estado not in ESTADOS_ALTA_ABIERTOS:
        raise ValueError(
            "estado inicial debe ser pre_reserva o pendiente_pago"
        )

    u = db.get(Unidad, body.unidad_id)
    if not u:
        raise ValueError("Unidad no encontrada")
    if not u.disponible_para_reserva:
        raise ValueError("La unidad no está en modo reservable")

    if not disponibilidad_service.estadia_libre(
        db, body.unidad_id, body.check_in, body.check_out
    ):
        raise ValueError("Hay solape con otra reserva en esas fechas")

    cot = pricing_engine.cotizar(
        db,
        u,
        body.check_in,
        body.check_out,
        promo=body.promo,
        aplicar_precio_efectivo=body.aplicar_precio_efectivo,
    )

    r = Reserva(
        unidad_id=body.unidad_id,
        check_in=body.check_in,
        check_out=body.check_out,
        estado=body.estado,
        origen=body.origen,
        huesped_nombre=body.huesped_nombre,
        huesped_telefono=body.huesped_telefono,
        huesped_email=body.huesped_email,
        personas=body.personas,
        precio_total=cot.total,
        notas_internas=body.notas_internas,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def crear_operacion(db: Session, body: ReservaOperacionCreate) -> tuple[Reserva, str, str]:
    """Reserva confirmada manual — bloquea calendario e iCal export."""
    u = db.get(Unidad, body.unidad_id)
    if not u:
        raise ValueError("Unidad no encontrada")
    if not u.disponible_para_reserva:
        raise ValueError("La unidad no está en modo reservable")

    if not disponibilidad_service.estadia_libre(
        db, body.unidad_id, body.check_in, body.check_out
    ):
        raise ValueError("Hay solape con otra reserva en esas fechas")

    cot = pricing_engine.cotizar(
        db,
        u,
        body.check_in,
        body.check_out,
        promo=body.promo,
        aplicar_precio_efectivo=body.aplicar_precio_efectivo,
    )

    r = Reserva(
        unidad_id=body.unidad_id,
        check_in=body.check_in,
        check_out=body.check_out,
        estado="confirmada",
        origen=body.origen,
        huesped_nombre=body.huesped_nombre,
        huesped_telefono=body.huesped_telefono,
        personas=body.personas,
        precio_total=cot.total,
        notas_internas=body.notas_internas,
    )
    db.add(r)
    db.commit()
    db.refresh(r)

    codigo = codigo_reserva_amigable(r.id)
    msg = _mensaje_confirmacion_huesped(
        codigo=codigo,
        huesped=body.huesped_nombre,
        unidad_nombre=u.nombre,
        check_in=body.check_in,
        check_out=body.check_out,
        total=cot.total,
    )
    return r, codigo, msg


def obtener(db: Session, reserva_id: str) -> dict | None:
    r = db.get(Reserva, reserva_id)
    return _to_out(r) if r else None


def listar(
    db: Session,
    unidad_id: str | None,
    desde: date | None,
    hasta: date | None,
) -> list[dict]:
    q = db.query(Reserva).order_by(Reserva.check_in.desc())
    if unidad_id:
        q = q.filter(Reserva.unidad_id == unidad_id)
    if desde is not None and hasta is not None:
        q = q.filter(
            Reserva.check_in < hasta,
            Reserva.check_out > desde,
        )
    return [_to_out(x) for x in q.limit(500).all()]


def patch(db: Session, reserva_id: str, body: ReservaPatch) -> Reserva | None:
    r = db.get(Reserva, reserva_id)
    if not r:
        return None
    cambios = body.model_dump(exclude_unset=True)
    if not cambios:
        raise ValueError("Sin campos para actualizar")
    if "estado" in cambios:
        r.estado = cambios["estado"]
    if "notas_internas" in cambios:
        r.notas_internas = cambios["notas_internas"]
    if "id_externo_ota" in cambios:
        r.id_externo_ota = cambios["id_externo_ota"]
    db.commit()
    db.refresh(r)
    return r
