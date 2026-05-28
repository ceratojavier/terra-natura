# Sitio único + panel del dueño

## Una sola web pública

| Qué | Carpeta | URL en producción |
|-----|---------|-------------------|
| **Sitio oficial** | `frontend/public/` | https://alpinasterranatura.com.ar |
| Carpeta `web/` (Next.js) | Solo desarrollo futuro | **No** se publica en el dominio |

Cada cambio en `frontend/public/` que subís a la rama `main` de GitHub dispara el workflow **Deploy sitio web (Pages)** y actualiza el dominio.

## Panel del dueño (reservas y calendario)

| Acceso | URL |
|--------|-----|
| **Menú del equipo** | https://alpinasterranatura.com.ar/panel.html |
| Atajo (si el servidor Python está activo) | https://alpinasterranatura.com.ar/panel |

Desde el panel:

1. **Calendario de ocupación** — vista por unidad (verde libre / rojo ocupado).
2. **Reservas** — lista con fechas, huésped, origen (web, Booking, etc.).
3. **Sincronizar Booking** — baja los calendarios iCal de Booking y actualiza el PMS.
4. **Calendarios (export)** — enlaces para pegar en Airbnb u otras OTAs.

### Importante: GitHub Pages vs servidor completo

- **Solo GitHub Pages** sirve HTML, fotos y cotización estimada. El panel y Booking **necesitan** el programa PMS (FastAPI) encendido en un servidor.
- **Modo recomendado en tu PC:** doble clic en `local/inicia_servidor_interno.bat` → abrís http://localhost:8000/panel — ahí sí ves reservas y podés sincronizar Booking.
- **Modo producción completo:** una VM (Oracle, etc.) con `python -m backend.app` y el dominio apuntando a esa máquina **o** `apiBase` en `site-config.json` apuntando a esa API.

## Booking conectado

Los enlaces iCal de Booking están en `backend/services/ical_feeds_service.py` (5 unidades).

Sincronización manual: panel → **Sincronizar Booking ahora**.

Automática (cuando hay servidor): programar cada 6 h `POST /api/canales/sync-ical`.

## Mercado Pago y reserva web

Página pública: `/reservar.html` — cotizar y pagar seña si `apiBase` en `assets/data/site-config.json` apunta al servidor PMS.
