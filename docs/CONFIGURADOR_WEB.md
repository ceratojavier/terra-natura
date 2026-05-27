# Configurador web — instalador Terra Natura

## Abrir

1. Ejecutá `local/Abrir-Terra-Natura.bat` (o el ícono del escritorio).
2. Se abre: **http://127.0.0.1:8000/configurador**

También: `/entrar` redirige al configurador.

## Qué hace

- Guía **paso a paso** (Siguiente / Atrás / Adjuntar).
- Guarda en **`local/config-dueño.json`** (no va a Git).
- Sincroniza archivos legibles para Cursor:
  - `marketing/contexto/negocio.json`
  - `marketing/contexto/objetivos.json`
  - `marketing/contexto/redes.json`
  - `marketing/contexto/00_voz_marca.md`
- Aplica **canales** al PMS (Booking / solo directo).
- Escribe **YOUTUBE_API_KEY** en `.env` si la pegás en el paso YouTube.
- Subidas en **`local/setup-uploads/`**.

## Pasos del wizard

| # | Paso | Obligatorio |
|---|------|-------------|
| 1 | Bienvenida | No |
| 2 | Datos del complejo (WhatsApp, dirección) | Sí |
| 3 | Objetivos de marketing | Sí |
| 4 | Tarifas por inflación (verano + % baja) | Sí |
| 5 | Voz de marca | Sí |
| 6 | Instagram y redes | Sí |
| 7 | Fotos (adjuntar o carpeta multimedia) | Sí |
| 8 | Herramientas PC (ffmpeg, yt-dlp) | Sí |
| 9 | YouTube API | No |
| 10 | Canales de reserva | Sí |
| 11 | Agenda eventos | No |
| 12 | APIs opcionales (Meta, MP) | No |
| 13 | Resumen | — |

En cada paso: **«¿Cómo consigo esto?»** con instrucciones para el dueño.

## API (desarrollo)

- `GET /api/setup/estado`
- `GET /api/setup/paso/{id}`
- `PUT /api/setup/paso/{id}` — body `{ "valores": { ... } }`
- `POST /api/setup/paso/{id}/adjunto` — multipart
- `POST /api/setup/sincronizar-agenda`

## Después de configurar

Usá **Programa** (`/programa`) para YouTube, calendario y videos.  
Los agentes leen `marketing/contexto/` y `local/config-dueño.json`.
