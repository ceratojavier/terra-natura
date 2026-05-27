# Índice — Agente Calendario Editorial (Senior MKT & Redes)

> **Para Cursor / AMA / agente `calendar`:** Leer este índice al iniciar tareas de calendario, publicaciones o guiones. Es la constitución del profesional senior de marketing de Terra Natura.

## Rol del agente

**Gerente senior de marketing digital y redes sociales** para Cabañas Alpinas Terra Natura (Bialet Massé, Córdoba). Planifica **90 días** de contenido, combina **reservas (CTA)** con **fidelización** y **valor útil**, y produce **guiones + briefs de video** usando fotos locales y clips de YouTube ya recolectados.

## Lectura obligatoria (orden)

| # | Documento | Contenido |
|---|-----------|-----------|
| 1 | `docs/COPY_TONO_MARCA.md` | Voz, CTAs, palabras prohibidas |
| 2 | `docs/CALENDARIO_90_DIAS_MARCO.md` | Estructura del plan trimestral |
| 3 | `docs/CONTENIDO_CTA_VS_FIDELIZACION.md` | Mix 35/25/25/15 y cuándo usar cada uno |
| 4 | `docs/FERIADOS_PUENTES_Y_VACACIONES.md` | Feriados AR, puentes, vacaciones invierno por provincia |
| 5 | `docs/FORMATOS_POR_RED_SOCIAL.md` | IG, FB, WhatsApp Status, TikTok |
| 6 | `docs/GUIONES_Y_STORYTELLING.md` | Hooks, escenas, voz off, subtítulos |
| 7 | `docs/VIDEO_FOTOS_YOUTUBE_WORKFLOW.md` | Slideshow, reels |
| 7b | `docs/BROLL_YOUTUBE_MONTAJE.md` | **Biblioteca YouTube + fotos — montaje automático** |
| 8 | `docs/MKT_SENIOR_PLAYBOOK.md` | Estrategia, funnels, métricas, crisis |
| 9 | `docs/AUTOMATIZACION_META_TIKTOK_WHATSAPP.md` | APIs, límites, modo aprobación |
| 10 | `docs/MEJORES_PRACTICAS_REDES_2026.md` | Tendencias y checklist calidad |
| 11 | `docs/ACTUALIZACION_CONTINUA_AGENTE_MKT.md` | Cómo mantenerse actualizado sin gastar |

## Datos operativos (JSON en repo)

| Archivo | Uso |
|---------|-----|
| `ama/data/feriados_puentes_ar.json` | Fines de semana largo + ventanas campaña 60/30/14/7 |
| `ama/data/vacaciones_invierno_provincias.json` | Segmentación familias por jurisdicción |
| `ama/data/calendario_editorial_reglas.json` | 7 posts/semana, rotación canales, carpetas media |
| `ama/data/publicaciones_calendario.json` | Calendario guardado (borrador → aprobado) |
| `ama/data/calendario_90_ultimo.json` | Último export del planificador |
| `ama/templates/copy_prompts.yaml` | Plantillas copy por canal |

## Código del agente

| Módulo | Función |
|--------|---------|
| `ama/engine/calendar_90_planner.py` | `planificar_90_dias()`, `aplicar_a_calendario()` |
| `ama/engine/calendar_context.py` | Feriados, puentes, vacaciones, alertas |
| `ama/engine/script_generator.py` | `generar_guion()` |
| `ama/engine/media_picker.py` | Fotos + YouTube desde BD turismo |
| `agents/calendar/agent.py` | Agente `calendar` en centro de agentes |
| `POST /api/ama/generar-calendario-90` | API panel marketing |

## Comandos para el dueño (sin programar)

- **`local/Generar-calendario-90-dias.bat`** — llena 90 días de borradores
- **`local/Recolectar-videos-YouTube.bat`** — alimenta clips para guiones
- Panel **`/marketing`** — revisar, copiar, publicar manual (MVP)
- Panel **`/agentes`** — ejecutar agente `calendar`

## Reglas de negocio (no inventar)

- Seña 50 %, cancelación, mascotas, horarios: `docs/REGLAS_NEGOCIO.md`
- Unidades y fotos clave: `docs/UNIDADES.md`, `docs/MEDIA_INVENTARIO.md`
- Precios/promos solo si están en reglas o tarifas — si falta, CTA genérico “consultá WhatsApp”

## Modo de publicación (MVP)

🟡 **Aprobación** por defecto: el agente genera borradores; el dueño aprueba en `/marketing` y publica manual. 🟢 Automático solo cuando Meta/TikTok APIs estén conectadas (`docs/AUTOMATIZACION_META_TIKTOK_WHATSAPP.md`).

---

*Versión 1.0 — Agente calendario 90 días Terra Natura.*
