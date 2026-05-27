"""
Modelo de unidad (cabaña / suite) — totalmente configurable.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.config.database import Base


class Unidad(Base):
    """
    Cada fila = una unidad física del complejo.
    activa + alquilable + uso_modo determinan si entra al calendario y OTAs.
    """

    __tablename__ = "unidades"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # alpina | suite
    numero: Mapped[int] = mapped_column(Integer, nullable=False)

    # --- Interruptores maestros (lo que pedís poder cambiar) ---
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    """False = unidad apagada en todo el sistema."""

    alquilable: Mapped[bool] = mapped_column(Boolean, default=True)
    """False = no aparece en disponibilidad ni reservas (ej. transformada en salón)."""

    uso_modo: Mapped[str] = mapped_column(String(32), default="alquiler")
    """
    alquiler | salon_desayuno | salon_comedor | espacio_comun |
    mantenimiento | fuera_servicio | uso_familiar
    """

    visible_web: Mapped[bool] = mapped_column(Boolean, default=True)
    visible_ota: Mapped[bool] = mapped_column(Boolean, default=True)

    # --- Capacidad y venta ---
    capacidad_max: Mapped[int] = mapped_column(Integer, default=2)
    capacidad_recomendada: Mapped[int] = mapped_column(Integer, default=2)
    recomendado_parejas: Mapped[bool] = mapped_column(Boolean, default=True)

    # --- Características físicas ---
    planta: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pb_metros_cuadrados: Mapped[float | None] = mapped_column(Float, nullable=True)
    tiene_aire_acondicionado: Mapped[bool] = mapped_column(Boolean, default=False)
    color_detalle: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # --- Precios referencia (tarifas dinámicas en fase posterior) ---
    precio_verano_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    precio_verano_max: Mapped[float | None] = mapped_column(Float, nullable=True)

    notas_internas: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str | None] = mapped_column(String(64), nullable=True)

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def disponible_para_reserva(self) -> bool:
        return (
            self.activa
            and self.alquilable
            and self.uso_modo == "alquiler"
        )
