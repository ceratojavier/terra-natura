# Fuentes de la agenda de eventos — Terra Natura

El programa **no** se limita a Cosquín folklore. Recolecta feriados, puentes y eventos con **potencial de reserva en Bialet**: Punilla (Carlos Paz, La Falda, La Cumbre, Capilla del Monte), **Dique San Roque / La Estación** (electrónica), excursión **VGB · Alta Gracia · Córdoba/Kempes**. Reglas: `ama/data/criterios_eventos_cabanas.json` · confirmados: `ama/data/eventos_confirmados_ar.json`.

## Cómo funciona

1. Vos elegís **desde / hasta** en `/programa`.
2. **Actualizar eventos del período** ejecuta `ama/scrapers/event_hunter.py` y guarda `ama/data/eventos_agenda_cache.json`.
3. **Ver listado** muestra feriados, puentes (con días viernes–lunes y audiencia Córdoba vs Buenos Aires) y eventos.
4. **Calendario editorial** genera posts para **todo ese rango** (no “90 días” fijos).

## Actualización semanal

- Script: `local/Actualizar-agenda-eventos.bat` o `python -m backend.jobs.actualizar_agenda_semanal`
- Recomendado: **cada lunes** antes de revisar campañas.

## Configurador (paso 11)

En `/configurador` podés **activar o desactivar** cada fuente y agregar URLs propias.
Se guarda en `local/config-dueño.json` y `marketing/contexto/fuentes_eventos_config.json`.

## Registro de fuentes (JSON)

Archivo maestro: `ama/data/fuentes_agenda_eventos.json`

| Área | Ejemplos |
|------|----------|
| Oficial | Córdoba Turismo, Bialet Massé eventos, feriados Argentina |
| Medios | El Diario Carlos Paz, Carlos Paz Vivo, Diario Córdoba, La Voz |
| Deportes | Running Argentina, triatlón, rally ACTC, ciclismo FECO |
| Música | Kempes, Cosquín Rock/Folklore, Festival del Cuarteto |
| Datos locales | `fiestas_recurrentes_extendido.json`, `turismo_seed_data.py`, BD `turismo_eventos` |

## Puentes y público

`ama/engine/puente_travel_context.py` marca:

- **Cantidad de días** del puente (ej. viernes · sábado · domingo · lunes = 4 días).
- **Noches sugeridas** para reserva.
- **Audiencias por origen**: Córdoba (check-in viernes), Buenos Aires (check-in sábado), etc.

Eso alimenta el copy del calendario editorial (CTA distinto por segmento).

## Pendiente / mejoras V2

- Scrapers dedicados por fuente (Kempes agenda HTML, Running Argentina con fecha exacta).
- Confirmación manual de fechas `a_confirmar` desde el panel.
- Alertas cuando una fuente cambia una fecha oficial.
