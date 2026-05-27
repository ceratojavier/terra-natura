# Investigación eventos — dueño (guardado en el sistema)

> Fuente estructurada: `ama/data/investigacion_eventos_dueño.json`  
> Matriz publicaciones × persona: `ama/data/matriz_publicaciones_evento_persona.json`  
> Feriados/puentes 2026: `ama/data/feriados_puentes_ar.json` (Resolución JGM 164/2025)

## 1. Portales oficiales

| Fuente | Para qué |
|--------|----------|
| **Córdoba Turismo — Agenda** | Fechas exactas grillas (Barrancas Bermejas nov, Nueve Lunas Cosquín) |
| **Córdoba Turismo — Prensa** | Nombres oficiales (Tanti **Solar del Rock**, fines solidarios) |
| **Bialet Massé turismo** | Identidad Barrancas / Labios del Indio |

## 2. Medios regionales

| Fuente | Para qué |
|--------|----------|
| **El Diario de Carlos Paz** | Interés Turístico Provincial y fines de semana de festivales chicos |

## 3. Deportes

| Fuente | Para qué |
|--------|----------|
| **Código Aventura** | Trail / MTB — pico octubre Carlos Paz |
| **Desafío Río Pinto** (vía Córdoba Deportes) | MTB mayo — salida La Cumbre |

## Fines de semana largo 2026 (actualizado)

**Días no laborables turísticos:** 23-mar · 10-jul · 7-dic  

**XL (4 días):** Memoria 21–24 mar · 9 de Julio 9–12 jul · Inmaculada 5–8 dic  

Más: Carnaval, Semana Santa, 1° Mayo, 25 Mayo, San Martín, 12 Oct, Soberanía, Navidad.

Verificar cada trimestre en [argentina.gob.ar feriados 2026](https://www.argentina.gob.ar/jefatura/feriados-nacionales-2026).

## Publicaciones por buyer persona

El motor `ama/engine/evento_publicaciones.py` asigna, por cada evento:

- **Tipo** (puente, festival, deporte, local Bialet, Kempes…)
- **Personas** (pareja, familia, deportista, fan festival, Córdoba finde, BA puente)
- **Cronograma** (60, 45, 30… 3, 1 días antes) con formato y canal (IG reel, FB post, WA Status)

Aparece en la agenda del programa como `plan_publicaciones` al previsualizar cada evento.

---

*Actualizado desde configurador / investigación mayo 2026.*
