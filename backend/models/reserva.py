"""
Reserva — bloques [check_in, check_out) en fecha calendario.
check_out exclusivo (noche hasta la víspera del checkout).
"""
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.config.database import Base


ESTADOS_RESERVA = (
    "pre_reserva",
    "pendiente_pago",
    "confirmada",
    "checkin_hecho",
    "ocupada",
    "checkout_pendiente",
    "cerrada",
    "cancelada",
    "no_show",
)

# Ocupa calendario (anti overbooking salvo cerrada/cancelada)
ESTADOS_BLOQUEANTES = frozenset(
    {
        "pre_reserva",
        "pendiente_pago",
        "confirmada",
        "checkin_hecho",
        "ocupada",
        "checkout_pendiente",
    }
)


class Reserva(Base):
    __tablename__ = "reservas"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    unidad_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("unidades.id"), nullable=False
    )

    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)

    estado: Mapped[str] = mapped_column(String(24), nullable=False, default="pre_reserva")
    origen: Mapped[str] = mapped_column(String(24), nullable=False, default="web_directa")

    huesped_nombre: Mapped[str | None] = mapped_column(String(160), nullable=True)
    huesped_telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    huesped_email: Mapped[str | None] = mapped_column(String(120), nullable=True)

    personas: Mapped[int] = mapped_column(Integer, default=2)
    precio_total: Mapped[float] = mapped_column(Float, default=0.0)
    moneda: Mapped[str] = mapped_column(String(8), default="ARS")
    id_externo_ota: Mapped[str | None] = mapped_column(String(80), nullable=True)

    notas_internas: Mapped[str | None] = mapped_column(Text, nullable=True)

    creado_en: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    unidad = relationship("Unidad", backref="reservas")
