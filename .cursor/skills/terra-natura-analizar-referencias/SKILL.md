---
name: terra-natura-analizar-referencias
description: >-
  Analizar reels de referencia (Instagram/TikTok) y extraer receta de edición
  para Terra Natura — ritmo, gancho, cortes. No copiar video ajeno; adaptar
  estructura con fotos propias. Usar cuando el usuario pase links o MP4 de otras cabañas.
---

# Skill — Analizar referencias de reels

## Legal

- **Inspirar** estructura (gancho, duración de planos, texto, orden).
- **No** republicar el MP4 ni la música del reel ajeno.
- Salida Terra Natura = fotos del complejo + B-roll entorno.

## Si hay MP4 local

1. Usuario guarda reel en `marketing/sistema/referencias_reels/videos/`
2. Ejecutar: `python -m ama.engine.reel_reference_probe`
3. Leer `marketing/sistema/referencias_reels/indice.json`

## Si solo hay link o descripción del usuario

Completar `plantilla_referencia.yaml` con:

- hook (primeros 2 s)
- segundos por plano
- texto en pantalla (sí/no, dónde)
- secuencia observada (entorno → habitación → pileta → CTA)
- `preset_sugerido`: `clasico_cabana` | `rapido_trend` | `lento_emocional` | `antes_despues`

Merge manual en `indice.json` bajo `referencias`.

## Aplicar al próximo reel

- `estilo_activo` en indice.json → guiones usan `reel_style_library.py`
- Pedir generar video: `editorial_reel_builder` + `script_generator`

## Doc

`docs/BIBLIOTECA_ESTILOS_REELS_IG.md`
