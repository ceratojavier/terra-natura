# Tarifas — coeficiente de inflación variable

## Concepto (dueño)

1. **Base:** precio promedio del **último verano** (ene–feb), **sin inflación** cargada en el configurador.
2. **Al cotizar** cada noche, el motor multiplica por un **coeficiente que cambia según el mes** de esa noche.
3. **No es** un 30 % fijo para todo el año.

## Cómo se calcula el coeficiente

Para una fecha objetivo (ej. 15-jun-2026):

- Tramo: **jun-2025 → jun-2026** (mismo mes, interanual acumulado).
- Cada mes del tramo usa la **tasa mensual mediana REM** (BCRA, ~45 consultoras).
- Fórmula: `multiplicador = ∏ (1 + tasa_mensual/100)`.

Ejemplos distintos:

| Período | Tramo | Coef. distinto |
|---------|-------|----------------|
| Puente junio | jun-25 → jun-26 | Sí |
| Vacaciones julio | jul-25 → jul-26 | Sí (otro %) |
| Verano enero | ene-25 → ene-26 | Sí |

## Temporada baja

Sobre el precio **ya ajustado por coeficiente** del mes:

- Finde semana baja: `× porcentaje_baja` (ej. 0,80).
- Lun–jue baja: `× porcentaje_baja × (1 − 0,15)`.

## Fuentes de datos

- **REM BCRA** — XLSX mensual `tablas-relevamiento-expectativas-mercado-*.xlsx` (auto-descarga).
- Meses sin dato en el XLSX: tasa default 2,6 % (configurable en fallback).
- Cache: `local/inflacion_proyeccion_cache.json` (36 h).

## API

- `GET /api/setup/coeficiente-inflacion?fecha=2026-06-15`
- `POST /api/setup/inflacion-proyeccion/actualizar` — refresca serie REM
- Cotización: `POST /api/reservas/cotizar` — cada noche trae `coeficiente_inflacion_pct`

## Código

- `backend/services/inflacion_coeficiente_service.py`
- `backend/services/pricing_engine.py`
