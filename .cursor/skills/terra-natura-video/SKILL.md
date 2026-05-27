---
name: terra-natura-video
description: >-
  Agente Productor video Terra Natura: arma MP4 desde fotos locales y guion del
  Guionista. Usar después de tener guion_reel.md del día.
---

# Agente 4 — Productor video

## Entrada

- `marketing/resultados/YYYY-MM-DD/guion_reel.md`
- Fotos: `archivos multimedia/` (ver `docs/MEDIA_INVENTARIO.md`)

## Salida

- `ama/output/videos/TN_YYYY-MM-DD_reel.mp4`
- Actualizar ítem en `ama/data/publicaciones_calendario.json` con `video_ruta`

## Código

- `ama/video/editorial_reel_builder.py`
- `ama/video/slideshow_builder.py`
- Job agente: tarea `generar_videos_editoriales` en `agents/calendar/agent.py`

## Reglas

- Montaje **armónico**: alternar B-roll YouTube + fotos propias; fundidos entre escenas (`xfade` en `editorial_reel_builder.py`).
- No copy "Punilla" en textos del video; sí sierras, Bialet, lago San Roque.
- Música libre derechos en `ama/assets/music/`
- Marca: logo/texto según `ama/video/brand_frames.py`
- Doc dueño: `docs/VIDEO_REEL_ARMONICO.md`
- No usar material con copyright sin licencia
