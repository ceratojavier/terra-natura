# Grilla turística — Bialet Massé y zona

## Qué se guardó

Base de datos SQLite/PostgreSQL del PMS con 3 tablas:

| Tabla | Contenido |
|-------|-----------|
| `turismo_lugares` | Qué visitar todo el año (río, senderos, museo, Cosquín…) |
| `turismo_eventos` | Ferias, festivales, carnaval, feriados — **grilla por mes** |
| `turismo_contenidos` | Enlaces YouTube, Instagram, TikTok y webs para armar videos |

## Cómo verlo

- **Panel web:** http://127.0.0.1:8000/turismo
- **JSON exportado:** `agents/data/turismo/grilla_anual_2026.json`
- **API:** `GET /api/turismo/grilla?anio=2026`

## Actualizar datos

Doble clic: `local/Cargar-grilla-turismo.bat`  
O con el servidor: `POST /api/turismo/recolectar?force=true`

## YouTube (videos reales — API)

1. Seguí `docs/YOUTUBE_API_SETUP.md`
2. Poné `YOUTUBE_API_KEY` en `.env`
3. `local/Recolectar-videos-YouTube.bat` o botón en `/turismo`

Guarda: título, canal, miniatura, duración, vistas, URL, localidad.

## Instagram / TikTok

Solo enlaces de búsqueda en la base (sin API pública gratuita fiable).

## Uso para videos AMA

El agente **Contenido & Redes** incluye la tarea `grilla_turismo` que lee esta base y sugiere meses con más eventos para campañas.
