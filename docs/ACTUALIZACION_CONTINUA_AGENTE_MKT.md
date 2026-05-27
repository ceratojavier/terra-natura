# Actualización continua — Agente MKT senior

## Objetivo

Que el agente de calendario **no quede obsoleto** en APIs, formatos y tendencias, **sin depender de cursos pagos** obligatorios.

## Rutina mensual (30 min — dueño o dev)

1. Revisar `ama/data/feriados_puentes_ar.json` vs calendario oficial Argentina.
2. Actualizar `vacaciones_invierno_provincias.json` si cambian fechas escolares.
3. Ejecutar `POST /api/turismo/youtube/recolectar` para clips frescos.
4. Leer sección “Cambios” abajo en este doc (actualizar al final de cada revisión).

## Fuentes gratuitas recomendadas

| Tema | Fuente |
|------|--------|
| Meta IG/FB | [Meta for Business](https://www.facebook.com/business/news), [developers.facebook.com/docs](https://developers.facebook.com/docs) |
| TikTok | [TikTok for Business blog](https://www.tiktok.com/business/en/blog) |
| WhatsApp Business | [WhatsApp Business API docs](https://developers.facebook.com/docs/whatsapp) |
| Turismo AR | Turismo Córdoba, agenda Punilla, feriados Argentina.gob.ar |
| Hospitalidad | Revinate blog, Airbnb resource center (ideas, no copiar políticas) |

## Capacitación estructurada (auto-estudio)

### Nivel 1 — Operación Terra Natura (ya en repo)

- Leer índice `docs/AGENTE_CALENDARIO_REDES_INDICE.md` completo
- Practicar: generar 90 días → aprobar 5 posts → publicar manual

### Nivel 2 — Producción video

- MoviePy: README proyecto + `docs/VIDEO_FOTOS_YOUTUBE_WORKFLOW.md`
- CapCut o Canva free: un reel siguiendo guion JSON de una publicación

### Nivel 3 — APIs (cuando el dueño autorice tokens)

- Meta: crear app, probar POST página en sandbox
- YouTube: ya activo — revisar cuota en Google Cloud Console

### Nivel 4 — Medición

- Definir planilla simple: fecha post → consultas WA → reserva (origen)

## Qué documentar después de cada aprendizaje

Añadir bullet en **Cambios** con fecha:

```markdown
## Cambios
- 2026-05-20: IG aumentó duración ideal reel a X s — actualizar GUIONES si aplica.
```

## Integración con Cursor / IA

Al programar nuevas features, el dev indica al agente:

> “Leé `docs/AGENTE_CALENDARIO_REDES_INDICE.md` y el doc X antes de codificar.”

No sustituye leer reglas de negocio (`REGLAS_NEGOCIO.md`).

## Cursos de pago (opcional)

Solo si el dueño invierte: Meta Blueprint, TikTok Academy. **Resumen** de lo relevante volcar a `MEJORES_PRACTICAS_REDES_2026.md` — no guardar PDFs con login en repo.

## Cambios

- 2026-05-20: Creación del sistema calendario 90 días + agente `calendar` + 11 docs MKT.
