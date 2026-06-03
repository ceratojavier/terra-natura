# Instagram — feed, pilares y calendario Terra Natura

**Marca:** Cabañas Alpinas Terra Natura · Bialet Massé · sierras de Córdoba (sin “Punilla” en copy público).  
**Datos máquina:** `ama/data/instagram_feed_grilla_junio_2026.json` · **Motor:** `ama/engine/instagram_feed.py`

---

## Los 3 pilares del feed

| Pilar | Objetivo | Ejemplos de contenido |
|-------|----------|------------------------|
| **La experiencia** | Vender el deseo | Neblina en el parque, fuego, café al ventanal, atardecer pileta, silencio del arroyo |
| **Infraestructura** | Romper objeciones | Tour Reel por unidad, cocina, camas, WiFi, pet-friendly, estacionamiento |
| **Guía local** | Autoridad | Qué hacer con lluvia, restaurantes Bialet, trekking, lago San Roque |

Rotación sugerida en el feed: **Experiencia → Guía → Infra → Experiencia** (cada 3–4 posts).

---

## Highlights fijas (embudo)

| Highlight | Contenido |
|-----------|-----------|
| **Cabañas** | Alpina 1·2·3 + Suite 4·5 (15–30 s cada una) |
| **Ubicación** | Mapa, Autovía, 600 m lago, cómo llegar |
| **Reservas** | CTA WhatsApp + link web |
| **Experiencias** | Reseñas Google/Booking (capturas reales) |

---

## Grilla de 12 publicaciones (junio 2026)

Ver JSON con hooks, captions AIDA y ideas de historias. El agente Guionista puede tomar `titulo` + `pilar` de ahí al planificar el mes.

---

## Repositorios de referencia (prompts)

Clonados o documentados en `marketing/referencias/github/README.md`:

- [krishna-build/marketing-prompts](https://github.com/krishna-build/marketing-prompts) — hooks IG, storytelling
- [SabrinaRamonov/prompts](https://github.com/SabrinaRamonov/prompts) — plantilla Instagram Marketing Content
- [eigent-ai/agent-skills](https://github.com/eigent-ai/agent-skills) — instagram-posting, copywriting

**Terra Natura:** siempre cruzar con `docs/COPY_TONO_MARCA.md` y `ama/templates/copy_prompts.yaml`.

---

## ManyChat + WhatsApp

- Flujo comentario **INFO** / **PRECIO**: `docs/MANYCHAT_INSTAGRAM_FLUJO.md`
- Agente IA WhatsApp Business: `docs/WHATSAPP_BUSINESS_IA_MAXIMO.md` (conecta con `WHATSAPP_IA_PROMPT_MAESTRO.md`)

---

## Prompt de arranque (Director de Marketing — hotelería)

Usalo en Cursor/AMA con voz de marca cargada:

> Actuá como Director de Marketing de hotelería boutique en **Bialet Massé, sierras de Córdoba**. Complejo: **Terra Natura**, 5 unidades (3 alpinas pareja/familia + 2 suites). Público: parejas y familias que buscan desconectar.  
> Generá grilla mensual: 12 posts feed (formato cada uno), hook 3 s, caption AIDA en español rioplatense cordobés sutil, 3 ideas de historias interactivas por post. Pilares: Experiencia / Infraestructura / Guía local. Sin clichés ni “Punilla” como slogan.
