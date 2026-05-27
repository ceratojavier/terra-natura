# Marketing Terra Natura — estructura para Cursor (sin Claude API)

Sistema inspirado en:
- Video *«Creé un equipo de marketing con IA»* (Migue Baena): **contexto → sistema → resultados** + agentes + skills
- PDF HubSpot *«Cómo usar la IA para crear un plan de marketing»*: 8 bloques del plan
- Motor técnico existente: carpeta `ama/` (publicaciones, eventos, videos)

**IA:** Cursor Agent (plan $20) + **Skills** en `.cursor/skills/`  
**No usar:** API de Claude como motor del plan (solo Cursor).

## Carpetas

| Carpeta | Qué guardás vos | Qué hace Cursor |
|---------|-----------------|-----------------|
| `marketing/contexto/` | Datos del negocio (formulario / web prep) | Lee antes de estrategia o copy |
| **`docs/COPY_TONO_MARCA.md`** | **Voz, palabras sí/no, ejemplos** | **Fuente de verdad para tono** |
| `marketing/contexto/00_voz_marca.md` | Tu formulario de voz (espejo editable) | Igual que el doc de arriba |
| `marketing/contexto/FEED_INSTAGRAM_TERRA_NATURA.md` | Blueprint feed IG (refs @aldea_india, @callesdelasierra) | Pilares, highlights, ritmo semanal |
| `.cursor/rules/terra-natura-voz-marketing.mdc` | Regla automática Cursor | Aplica en cada chat del proyecto |
| `.cursor/skills/terra-natura-copy/` | Skill “pedime copy con la skill” | Invocación explícita |
| `marketing/plan/` | Plan HubSpot: FODA, buyer personas, canales… | Completa borradores; vos validás en «Interpretación» |
| `marketing/sistema/` | Referencias, plantillas, reglas | Skills y agentes reutilizables |
| `marketing/resultados/` | Entregables (oferta, landings, emails, posts) | Escribe aquí; no mezclar con contexto |
| `marketing/.cursor-skills-index.md` | — | Índice de qué skill usar para qué tarea |

## Los 8 archivos del plan (PDF HubSpot)

1. `plan/01_informacion_general.md` ← **en curso**
2. `plan/02_foda.md`
3. `plan/03_iniciativas_comerciales.md`
4. `plan/04_mercado_objetivo.md`
5. `plan/05_canales_marketing.md`
6. `plan/06_estrategia_mercado.md`
7. `plan/07_tecnologia_marketing.md`
8. `plan/08_presupuesto.md`

## Agentes Cursor (próximo paso)

Se definirán en `.cursor/skills/` y reglas en `AGENTS.md` § Marketing, por ejemplo:
- Estratega de oferta / posicionamiento
- Copy reservas directas
- Calendario editorial (enlaza con `ama/`)

## Web de preparación

**Configurador web (instalador):** `http://127.0.0.1:8000/configurador` — paso a paso, guarda en `local/config-dueño.json` y sincroniza `marketing/contexto/`.
