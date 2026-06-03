# Terra Natura — App operativa (React)

Interfaz interna para programa de marketing, agentes AMA y cola de publicación.

## Requisitos

- Node.js 20+ o 22+
- Backend FastAPI en `http://127.0.0.1:8000`

## Comandos

```bash
cd frontend/app
npm install
npm run dev      # http://localhost:5173/app/programa (proxy API)
npm run build    # genera dist/ para FastAPI en /app
```

## URLs con backend

| Ruta | Pantalla |
|------|----------|
| `/app/hoy` | Pantalla principal del dueño |
| `/app/plan` | Plan de marketing (zona + campañas) |
| `/app/publicaciones` | Revisar y subir a Instagram |
| `/app/configuracion` | Conexiones y módulos avanzados |

Atajos: `/programa` y `/entrar` → `/app/hoy`.

## Estructura

```
src/
  api/           # cliente fetch + tipos
  components/    # ui (shadcn-style) + layout
  pages/         # programa, agentes, marketing
```

Documentación de decisión: `docs/FRONT_STACK_DECISION.md`.
