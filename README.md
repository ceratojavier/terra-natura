# Terra Natura

## Centro de agentes (nuevo)

Tres agentes automatizados: **Channel Manager**, **CRM** y **Contenido (redes)**.

- Panel: `/agentes` al iniciar el servidor
- Detalle: `docs/ARQUITECTURA_AGENTES.md`

## PMS + web pública

**Cabañas Alpinas Terra Natura** · Bialet Massé · Córdoba.

## Arranque rápido

```bash
cd "Proyecto Terra Natura"
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
python -m backend.app
```

- **Centro de agentes:** [http://127.0.0.1:8000/agentes](http://127.0.0.1:8000/agentes)
- **Sitio web:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Landings campañas:** `/landings/parejas` · `/landings/familia` · `/landings/reserva-directa` · `/landings/punilla`
- **Guía huésped (TV / celular):** [http://127.0.0.1:8000/guia/](http://127.0.0.1:8000/guia/)
- **API PMS:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Estructura

| Carpeta | Uso |
|---------|-----|
| `frontend/public/` | HTML + CSS del sitio y landings |
| `guest-app/` | Guía interactiva editable (`data.json`) |
| `archivos multimedia/` | Fotos/videos por unidad y entorno (`docs/MEDIA_INVENTARIO.md`) |
| `backend/` | FastAPI · unidades · configuración |
| `docs/` | Reglas de negocio, tarifas, campañas, seguridad |

## Documentación clave

- `AGENTS.md` — visión técnica del proyecto
- `docs/REGLAS_NEGOCIO.md` — políticas y contacto público
- `docs/CAMPANAS_INSTAGRAM_LANDINGS.md` — Instagram → landings + UTMs
- `docs/SEGURIDAD_CREDENCIALES.md` — nunca commitear claves
- `docs/MEDIA_INVENTARIO.md` — mapa carpetas foto/video local
- `docs/GITHUB_PAGES_NIC_CLOUDFLARE.md` — publicar web + dominio `.com.ar`

## Multimedia (ñ en nombres)

Si en tu PC seguís viendo **`CABAÑA`** o **`ñ`** en archivos/carpetas de `archivos multimedia/`, ejecutá el script (primero con `--dry-run`):

`local/normalizar_nombres_sin_tilde.py` — ver `local/README_SCRIPTS.md`.

## Producción

Servir el mismo proceso `uvicorn` detrás de Nginx o Caddy con dominio propio y TLS (Cloudflare u otro). Copiá `frontend/public` y `guest-app` junto al backend o usá el mismo contenedor.
