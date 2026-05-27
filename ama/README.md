# AMA — Agente de Marketing Autónomo

**Estado:** MVP usable (calendario, copy, video local, sugerencias WhatsApp para copiar).

| Componente | Archivo | Estado |
|------------|---------|--------|
| Calendario publicaciones | `storage/calendar_store.py` + `data/publicaciones_calendario.json` | Activo |
| Generador de textos | `engine/content_strategist.py` + `templates/copy_prompts.yaml` | Activo |
| Plan semanal | `engine/season_planner.py` + `data/feriados_ar.json` | Activo |
| Video slideshow | `video/slideshow_builder.py` (MoviePy opcional) | Activo |
| Chat sugerencias | `chat/responder.py` | Activo |
| Publicar en Meta | `publishers/` (futuro) | Pendiente |

**Panel:** `/marketing` en el mismo servidor que el PMS.

**Dueño:** `docs/AMA_PASO_A_PASO.md`

## Videos generados (WhatsApp / redes)

| Dónde | Qué hay |
|-------|---------|
| `ama/output/videos/` | MP4 finales + textos para copiar en WhatsApp |
| `archivos multimedia/videos marketing/` | Copia del mismo video (más fácil de encontrar) |

**Abrir carpeta:** doble clic en `local/Abrir-carpeta-videos.bat`
