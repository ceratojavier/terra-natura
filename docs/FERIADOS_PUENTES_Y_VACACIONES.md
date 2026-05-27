# Feriados, puentes y vacaciones de invierno

## Fuentes de datos en el proyecto

- `ama/data/feriados_ar.json` — feriados nacionales simples
- `ama/data/feriados_puentes_ar.json` — **fines de semana largo** + ventanas de campaña
- `ama/data/vacaciones_invierno_provincias.json` — receso escolar por jurisdicción

**Actualizar cada año** cuando publique el calendario oficial (Argentina.gob.ar / ministerios provinciales).

## Fines de semana largo 2026 (campaña reservas)

| Ventana | Fechas aprox. | Noches sugeridas | Hook |
|---------|---------------|------------------|------|
| Carnaval | 14–17 feb | 3 | Puente pileta + parque |
| Semana Santa | 2–5 abr | 3 | Escapada cerca del lago |
| 1° Mayo | 1–3 may | 2 | Familia o pareja |
| 25 Mayo | 23–25 may | 3 | Reserva directa |
| Güemes | 15–17 jun | 2 | Tarifa accesible |
| San Martín | 15–17 ago | 3 | Invierno + feriado |
| 12 Oct | 10–12 oct | 3 | Primavera vista valle |
| Soberanía | 20–22 nov | 2 | Suite con A/A |
| Navidad | 23–28 dic | 4 | Celebración en complejo |

## Ventanas de publicación (automatizable)

Para cada puente, programar posts en:

- **−60 días:** preventa suave (“agendá el puente de …”)
- **−30 días:** disponibilidad + beneficio unidad
- **−14 días:** urgencia moderada + CTA WhatsApp
- **−7 días:** último llamado (solo si hay stock real)

Implementado en `calendar_context.alertas_campana_proximas()`.

## Vacaciones de invierno por provincia (2026 referencia)

| Jurisdicción | Inicio | Fin | Ángulo copy |
|--------------|--------|-----|-------------|
| Córdoba | 13 jul | 31 jul | Familias cordobesas — Alpinas |
| CABA / PBA | 18 jul | 1 ago | Salir de la ciudad — 2 h |
| Santa Fe / ER | 20 jul | 3 ago | Escapada corta |
| Mendoza | 13 jul | 27 jul | Cambio de paisaje |

**Segmentación ads (V2):** Meta por provincia en fechas de receso; copy del JSON `mensaje_campana`.

## Bloques promo invierno

- **Preventa junio:** lun–jue −X % (definir en `REGLAS_NEGOCIO.md`)
- **Pico julio Córdoba:** destacar capacidad flexible Alpinas con menores

## Qué hace el agente con esto

1. `evento_en_fecha()` marca el día como puente/feriado/vacaciones
2. `calendar_90_planner` sube prioridad **cta_reserva** y ajusta ángulo (familia/evento)
3. `copy_hook` del JSON entra al cuerpo del post
4. Alertas en ciclo diario agente `calendar`

## Verificación humana obligatoria

Los puentes **trasladados** por decreto pueden cambiar. Antes de campaña paga, el dueño confirma fechas oficiales.
