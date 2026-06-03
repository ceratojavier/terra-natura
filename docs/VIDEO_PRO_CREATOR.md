# Video Pro Creator

App premium para generar prompts de vídeo cinematográficos (es-ES) y animar fotos con **Google Veo 3.1**.

## Acceso

- Con servidor Terra Natura: **http://127.0.0.1:8000/video-pro/**
- Desde la app del dueño: menú **Video Pro** o botón en **Hoy** → Configuración
- Acceso directo Windows: `local\Abrir-Video-Pro.bat`
- Desarrollo: `cd frontend/video-pro-creator && npm run dev` → http://localhost:5174/video-pro/

## Compilar

```powershell
cd frontend\video-pro-creator
npm install
npm install tailwindcss @tailwindcss/vite lucide-react
npm run build
```

## Veo (generación automática de vídeo)

En `.env` del proyecto:

```
GOOGLE_AI_API_KEY=tu_clave
# o GEMINI_API_KEY=
VEO_MODEL=veo-3.1-generate-preview
```

```powershell
pip install google-genai
```

Sin clave: la app igual genera prompts en español para copiar en [Google AI Studio](https://aistudio.google.com/).

## Despliegue (Render / Docker)

El `Dockerfile` compila **app operativa** y **Video Pro Creator** y sirve:

- `/app/hoy` — panel dueño
- `/video-pro/` — generador de prompts + Veo

Variables en el servicio: `GOOGLE_AI_API_KEY` o `GEMINI_API_KEY`, opcional `VEO_MODEL`.

Compilar solo en local:

```powershell
local\Compilar-video-pro.bat
local\Compilar-app-interna.bat
```

## Flujos

1. **Vídeo desde imagen** — foto + prompt de movimiento → enriquecimiento + Veo.
2. **Crear desde cero** — 4 pasos (personaje, ambiente, luz, estilo) → resumen + prompt + variantes.

## API

- `GET /api/video-pro/estado`
- `POST /api/video-pro/generar-prompt`
- `POST /api/video-pro/imagen-a-video` (multipart)
- `GET /api/video-pro/archivo?ruta=...`
