from typing import Any, Literal

from pydantic import BaseModel


class ConfigUpdate(BaseModel):
    valor: dict[str, Any]
    merge: bool = True


class DesayunoUpdate(BaseModel):
    habilitado: bool | None = None
    incluido_en_tarifa: bool | None = None
    precio_por_persona_ars: float | None = None
    horario_inicio: str | None = None
    horario_fin: str | None = None
    unidad_salon_id: str | None = None
    mensaje_cuando_no: str | None = None


class CanalesUpdate(BaseModel):
    modo_solo_reserva_directa: bool | None = None
    booking_habilitado: bool | None = None
    airbnb_habilitado: bool | None = None
    web_directa_habilitada: bool | None = None


class Suite4ReglasUpdate(BaseModel):
    modo: Literal["independiente", "hibrido", "solo_salon"] | None = None
