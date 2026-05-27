"""
Actualización de serie REM — delega en inflacion_coeficiente_service.

El % ya no es constante: ver coeficiente_interanual_mismo_mes(fecha).
"""
from __future__ import annotations

from typing import Any

from backend.services.inflacion_coeficiente_service import (
    actualizar_serie_rem,
    coeficiente_interanual_mismo_mes,
    vista_previa_periodos,
)


def actualizar_proyeccion(forzar: bool = False) -> dict[str, Any]:
    """Descarga REM y guarda serie mensual (cache)."""
    return actualizar_serie_rem(forzar=forzar)


def obtener_proyeccion(refrescar_si_viejo: bool = True) -> dict[str, Any]:
    from datetime import date

    from backend.services.inflacion_coeficiente_service import _leer_cache

    cache = _leer_cache()
    if refrescar_si_viejo and not cache:
        cache = actualizar_serie_rem(forzar=True)
    elif not cache:
        cache = actualizar_serie_rem(forzar=True)

    ej_hoy = coeficiente_interanual_mismo_mes(date.today())
    return {
        **cache,
        "modelo": "coeficiente_variable_por_periodo",
        "nota": "Cada fecha de estadía tiene su propio coeficiente (mismo mes año anterior → fecha).",
        "ejemplo_hoy": ej_hoy,
    }
