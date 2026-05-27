---
name: terra-natura-distribuidor
description: >-
  Agente Distribuidor Terra Natura: publica contenido aprobado en IG, FB, Google
  Business y WhatsApp Status. Usar solo con credenciales Meta en .env y modo
  aprobación cumplido.
---

# Agente 5 — Distribuidor (redes)

## Estado

**Fase 1 (hoy):** preparar paquete para copiar/pegar (caption + video + horario).  
**Fase 2:** `ama/publishers/meta_publisher.py` + cola `estado=aprobado`.

## Entrada

- Video y captions del día en `marketing/resultados/YYYY-MM-DD/`
- Post en `ama/data/publicaciones_calendario.json` con `estado: aprobado`

## Canales objetivo

| Canal | MVP | Automático |
|-------|-----|------------|
| Instagram | Copiar desde panel /marketing | Meta Graph API |
| Facebook | Idem | Meta Graph API |
| Google Business | Post manual | API GBP |
| WhatsApp Status | Subir video desde celular o API | Cloud API / n8n |

## Documentación

- `docs/AUTOMATIZACION_META_TIKTOK_WHATSAPP.md`
- Modos 🟢/🟡 en `AGENTS.md`

## Seguridad

- Tokens solo en `.env` — nunca en el repo.
