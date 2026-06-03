# Automatización del flujo Reel (calendario → Instagram)

Diagrama acordado y qué hace el sistema hoy vs qué sigue manual.

---

## Tabla: automático vs manual

| Paso | Estado | Cómo |
|------|--------|------|
| Calendario 3 jun — ítem Reel arroyo | **Auto** | `ama/engine/piezas_editoriales.py` + plan editorial |
| Modal: copy + guion escenas | **Auto** | Abrir pieza en Calendario/Plan → `desarrollar_pieza` + `guion_produccion` |
| Escenas YouTube — buscar + inicio/fin | **Manual** | Vos marcás en el panel (API guarda en `ama/data/guiones_produccion/`) |
| Fotos por escena | **Semi** | Auto-sugeridas con justificación; podés cambiar ruta en PATCH escena |
| Generar video (MP4) | **Auto** | Botón en modal → `POST /api/ama/guion-produccion/render` |
| Revisar MP4 | **Manual** | Descargás/abrís desde `ama/output/video/` o carpeta visible del panel |
| Enviar a Publicaciones | **Auto** | Botón **Enviar a publicaciones** → `POST /api/ama/pieza/enviar-publicaciones` |
| Aprobar en Publicaciones | **Manual** (modo 🟡) | Panel `/publicaciones` |
| Subir Reel a Instagram | **Condicional** | **Auto** si `META_*` + URL pública del video; si no, **manual** en la app IG |
| WhatsApp / ManyChat | **Docs listos** | Ver `MANYCHAT_INSTAGRAM_FLUJO.md` y `WHATSAPP_BUSINESS_IA_MAXIMO.md` |

---

## Probar hoy: Reel 3 de junio (arroyo)

1. Panel local: `http://127.0.0.1:8000/app/` → **Calendario** o **Plan**.
2. Abrí la pieza del **3/06** (*El sonido del arroyo…*).
   - `hito_id`: `editorial-evergreen`
   - `pieza_id`: `editorial|2026-06-03`
3. En el modal: revisá copy IG → **Generar guion de producción** si falta.
4. Por cada escena YouTube: buscá en YT, pegá ID y **inicio/fin** en segundos.
5. **Generar video** → esperá el MP4.
6. **Enviar a publicaciones** → te lleva a la cola.
7. **Publicaciones** → Aprobá → Publicar (o subí el Reel a mano en Instagram).

> **Nota:** «Preparar publicación de hoy» en **Hoy** usa otro motor (`planificar_dia`). Para el título del calendario editorial, usá siempre la pieza del día en Calendario/Plan.

---

## Cotización 2026 (pricing)

El motor `backend/services/pricing_engine.py` usa por defecto:

- **Alta / julio / findes largos:** Alpina **$120.000** · Suite **$100.000**
- **Resto (media/baja en calendario):** Alpina **$100.000** · Suite **$85.000**
- **Julio, 6+ noches:** promo **5+1** automática (`promo=auto` por defecto)
- **Mayo–junio baja, 5+ noches:** **4 paga 5** automática

Config en PMS: clave `tarifas_promociones` → `usar_calendario_comercial_2026: true`, `auto_promos_comercial_2026: true`.

---

## Próximos automatismos (backlog)

- Unificar «Preparar hoy» con la pieza editorial del día.
- Recordatorio si falta video antes de aprobar.
- Subida IG automática con URL del MP4 en servidor Oracle (no solo GitHub Pages).
