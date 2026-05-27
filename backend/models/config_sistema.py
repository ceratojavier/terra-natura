"""
Configuración clave-valor del complejo (desayuno, canales, seña, etc.)
"""
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.config.database import Base


class ConfigSistema(Base):
    __tablename__ = "config_sistema"

    clave: Mapped[str] = mapped_column(String(64), primary_key=True)
    valor: Mapped[str] = mapped_column(Text, nullable=False)  # JSON serializado
    categoria: Mapped[str] = mapped_column(String(32), default="general")
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
