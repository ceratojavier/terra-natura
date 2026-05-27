# Automatización — Meta, TikTok, WhatsApp

## Estado MVP Terra Natura

| Canal | Automatización | Modo actual |
|-------|----------------|-------------|
| Instagram / Facebook | Meta Graph API | Manual copy desde `/marketing` |
| WhatsApp Status | Cloud API / enlaces | Manual |
| TikTok | Marketing API / upload | Manual |
| YouTube | Solo **recolección** Data API | Activo |

**Modo por defecto:** 🟡 **Aprobación** (`ama_config.json` → `modo_publicacion: aprobacion`).

## Meta (Instagram + Facebook)

### Requisitos

1. Cuenta **Instagram Business** vinculada a **Facebook Page**
2. App en [developers.facebook.com](https://developers.facebook.com)
3. Permisos: `pages_manage_posts`, `instagram_content_publish`
4. Token larga duración en `.env` (nunca commitear)

### Variables `.env` (futuro)

```
META_PAGE_ACCESS_TOKEN=
META_IG_USER_ID=
```

### Módulo previsto

`ama/publishers/meta_publisher.py` — publicar imagen/video + caption desde `publicaciones_calendario.json` con estado `aprobado`.

### Límites

- Rate limits por app — espaciar publicaciones programadas ≥15 min
- Reels: video MP4 9:16, duración según IG rules

## WhatsApp

### Status (hoy)

Dueño publica desde celular con texto generado por AMA.

### Cloud API (V2)

- `WHATSAPP_VERIFY_TOKEN`, token Business
- Webhook en FastAPI para consultas → agente CRM
- Plantillas HSM para confirmación reserva (requiere aprobación Meta)

## TikTok

### Opciones

1. **Manual** (MVP): export reel → app TikTok → programar
2. **TikTok Marketing API** / Content Posting API (requiere app audit)

### Buenas prácticas API

- OAuth usuario creador de la cuenta cabaña
- No spam diario — respetar calendario 90 (3/semana TikTok)

## Programación (cron)

| Job | Frecuencia | Acción |
|-----|-----------|--------|
| `run_daily_agents.py` | 08:00 ART | channels → calendar → crm → content |
| Recolectar YouTube | semanal | turismo clips |
| Publicar aprobados | cuando exista meta_publisher | posts `estado=aprobado` del día |

## Seguridad

Ver `docs/SEGURIDAD_CREDENCIALES.md`. Rotar tokens si se exponen en chat.

## Checklist antes de activar auto-publicación

- [ ] 2 semanas de borradores aprobados sin error de tono
- [ ] Fotos siempre del complejo
- [ ] Legal promos y seña correctos
- [ ] Pausa automática si `channels` reporta 100 % ocupación finde
