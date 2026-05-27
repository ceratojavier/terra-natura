# Agentes Terra Natura

**Visión completa (objetivo final):** `docs/VISION_AGENTES_TERRA_NATURA.md`  
Guion → video → publicar en redes + CRM + channel manager.

## Cuatro agentes ejecutables (Python)

| ID | Carpeta | Qué hace hoy | Publica solo |
|----|---------|--------------|--------------|
| `channels` | `channels/` | OTAs, iCal, ocupación 7d | No |
| `calendar` | `calendar/` | Plan 90d, guiones, **generar videos** | No |
| `crm` | `crm/` | Leads, borradores WhatsApp | No |
| `content` | `content/` | Calendario AMA, alertas, coherencia | No |

**Panel:** http://127.0.0.1:8000/agentes  
**Ciclo:** `local/Ejecutar-agentes-diario.bat` → `agents/core/orchestrator.py`

## Skills Cursor (diseño / instrucciones — plan $20)

| Skill | Rol |
|-------|-----|
| `terra-natura-copy` | Captions y tono |
| `terra-natura-guionista` | Guion del día |
| `terra-natura-video` | MP4 desde fotos |
| `terra-natura-distribuidor` | Publicación (API pendiente) |

## Pendiente para objetivo final

- Agente **Pipeline diario** unificado (guion + video + cola publicación).
- `ama/publishers/meta_publisher.py` + WhatsApp Status API.

**Docs:** `docs/ARQUITECTURA_AGENTES.md` · `docs/AUTOMATIZACION_META_TIKTOK_WHATSAPP.md`
