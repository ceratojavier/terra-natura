"""
Base de datos turismo — lugares, eventos anuales, contenido (YouTube/IG/TikTok/web).
Para grilla editorial y futuros videos AMA.
"""
from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.config.database import Base


class TurismoLugar(Base):
    __tablename__ = "turismo_lugares"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    localidad: Mapped[str] = mapped_column(String(120), nullable=False, default="Bialet Massé")
    categoria: Mapped[str] = mapped_column(String(40), nullable=False)  # naturaleza, cultura, etc.
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    distancia_km_bialet: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)  # csv
    fuente_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    apto_video: Mapped[bool] = mapped_column(Boolean, default=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class TurismoEvento(Base):
    __tablename__ = "turismo_eventos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nombre: Mapped[str] = mapped_column(String(220), nullable=False)
    localidad: Mapped[str] = mapped_column(String(120), nullable=False)
    categoria: Mapped[str] = mapped_column(String(40), nullable=False)
    # Fechas concretas (edición 2026) o ventana recurrente
    fecha_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    mes_inicio: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-12 recurrente
    mes_fin: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dia_aprox: Mapped[str | None] = mapped_column(String(80), nullable=True)  # ej. "3er sábado enero"
    anio_referencia: Mapped[int] = mapped_column(Integer, default=2026)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    distancia_km_bialet: Mapped[float | None] = mapped_column(Float, nullable=True)
    entrada: Mapped[str | None] = mapped_column(String(120), nullable=True)  # gratis, paga, etc.
    fuente_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    apto_video: Mapped[bool] = mapped_column(Boolean, default=True)
    prioridad: Mapped[int] = mapped_column(Integer, default=5)  # 1=alta
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class TurismoContenido(Base):
    __tablename__ = "turismo_contenidos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    plataforma: Mapped[str] = mapped_column(String(20), nullable=False)  # youtube, instagram, tiktok, web
    url: Mapped[str] = mapped_column(String(600), nullable=False)
    titulo: Mapped[str | None] = mapped_column(String(300), nullable=True)
    canal_autor: Mapped[str | None] = mapped_column(String(200), nullable=True)
    localidad: Mapped[str | None] = mapped_column(String(120), nullable=True)
    evento_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    lugar_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    calidad: Mapped[str | None] = mapped_column(String(20), nullable=True)  # alta, media, busqueda
    verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    youtube_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duracion_segundos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vistas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    publicado_en: Mapped[datetime | None] = mapped_column(nullable=True)
    creado_en: Mapped[datetime] = mapped_column(default=datetime.utcnow)
