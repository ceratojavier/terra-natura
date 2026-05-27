from typing import Literal

from pydantic import BaseModel, Field

UsoModo = Literal[
    "alquiler",
    "salon_desayuno",
    "salon_comedor",
    "espacio_comun",
    "mantenimiento",
    "fuera_servicio",
    "uso_familiar",
]


class UnidadUpdate(BaseModel):
    nombre: str | None = None
    activa: bool | None = None
    alquilable: bool | None = None
    uso_modo: UsoModo | None = None
    visible_web: bool | None = None
    visible_ota: bool | None = None
    capacidad_max: int | None = Field(None, ge=1, le=12)
    capacidad_recomendada: int | None = Field(None, ge=1, le=12)
    recomendado_parejas: bool | None = None
    tiene_aire_acondicionado: bool | None = None
    color_detalle: str | None = None
    precio_verano_min: float | None = None
    precio_verano_max: float | None = None
    notas_internas: str | None = None
