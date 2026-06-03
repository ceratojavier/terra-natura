from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from backend.models.reserva import ESTADOS_RESERVA

_ESTADOS_SET = frozenset(ESTADOS_RESERVA)


class PagarPreferenciaRequest(BaseModel):
    unidad_id: str
    check_in: date
    check_out: date
    huesped_nombre: str = Field(min_length=2, max_length=80)
    huesped_email: str = Field(min_length=5, max_length=120)
    personas: int = Field(default=2, ge=1, le=6)

    @model_validator(mode="after")
    def fechas_validas(self):
        if self.check_out <= self.check_in:
            raise ValueError("check_out debe ser posterior a check_in")
        return self


class CotizarRequest(BaseModel):
    unidad_id: str
    check_in: date
    check_out: date
    promo: Literal["ninguna", "3x2", "4x3", "5mas1", "4paga5", "auto"] = "auto"
    aplicar_precio_efectivo: bool = False

    @model_validator(mode="after")
    def checkout_posterior(self):
        if self.check_out <= self.check_in:
            raise ValueError("check_out debe ser posterior a check_in (al menos una noche)")
        return self


class NochePrecio(BaseModel):
    fecha: date
    es_finde_sem_baja: bool
    temporada: Literal["verano_alta", "invierno_alta", "media_baja"]
    precio_noche: float
    coeficiente_inflacion_pct: float | None = None
    multiplicador_inflacion: float | None = None


class CotizarResponse(BaseModel):
    unidad_id: str
    noches: int
    desglose: list[NochePrecio]
    subtotal_sin_promo: float
    descuento_promo: float
    descuento_efectivo: float
    total: float
    promos_aplicadas: list[str]


class ReservaCreate(BaseModel):
    unidad_id: str
    check_in: date
    check_out: date
    origen: str = Field(default="web_directa")
    huesped_nombre: str | None = None
    huesped_telefono: str | None = None
    huesped_email: str | None = None
    personas: int = Field(ge=1, le=12, default=2)
    estado: str = Field(default="pre_reserva")
    promo: Literal["ninguna", "3x2", "4x3", "5mas1", "4paga5", "auto"] = "auto"
    aplicar_precio_efectivo: bool = False
    notas_internas: str | None = None

    @model_validator(mode="after")
    def fechas_consistentes(self):
        if self.check_out <= self.check_in:
            raise ValueError("check_out debe ser posterior a check_in")
        return self


class ReservaOut(BaseModel):
    id: str
    unidad_id: str
    check_in: date
    check_out: date
    estado: str
    origen: str
    huesped_nombre: str | None
    personas: int
    precio_total: float
    moneda: str


class ReservaPatch(BaseModel):
    estado: str | None = Field(default=None)
    notas_internas: str | None = Field(default=None, max_length=8000)
    id_externo_ota: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def algun_campo(self):
        if (
            self.estado is None
            and self.notas_internas is None
            and self.id_externo_ota is None
        ):
            raise ValueError("Indicá al menos un campo a actualizar")
        return self

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in _ESTADOS_SET:
            raise ValueError(f"estado inválido. Valores: {sorted(_ESTADOS_SET)}")
        return v

