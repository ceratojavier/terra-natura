# Desplegar API del cotizador (producción)

La web en **GitHub Pages** (`alpinasterranatura.com.ar`) es estática. El cotizador real usa la API FastAPI (`POST /api/cotizar`).

## Opción A — Render (recomendada, ~15 min)

1. Entrá a [render.com](https://render.com) con tu cuenta GitHub (`ceratojavier`).
2. **New → Blueprint** → elegí el repo `terra-natura`.
3. Render lee `render.yaml` y crea el servicio **`terra-natura-api`**.
4. Cuando el deploy esté **Live**, probá:  
   `https://terra-natura-api.onrender.com/health`  
   `https://terra-natura-api.onrender.com/api/public/motor-reserva`
5. En `frontend/public/assets/data/site-config.json` ya está:  
   `"apiBase": "https://terra-natura-api.onrender.com"`
6. Publicá el sitio:  
   `powershell -ExecutionPolicy Bypass -File scripts\publicar-sitio-gh-pages.ps1`

**Nota:** el plan free de Render “duerme” tras inactividad; la primera cotización puede tardar ~30 s en despertar.

### Sync Booking automático (Render)

Con el deploy actual, la API ejecuta **import iCal cada 15 min** al arrancar y en background (`ICAL_SYNC_INTERVAL_MIN`).

Variables opcionales en Render → Environment:

| Variable | Uso |
|----------|-----|
| `WHATSAPP_VERIFY_TOKEN` | Verificación webhook Meta |
| `WHATSAPP_CLOUD_TOKEN` | Enviar avisos al dueño + responder clientes |
| `WHATSAPP_PHONE_NUMBER_ID` | ID del número Business |
| `WHATSAPP_OWNER_PHONE` | Avisos reserva Booking (default 5493541571190) |

Webhook WhatsApp en Meta Developers:  
`https://terra-natura-api.onrender.com/api/webhooks/whatsapp`

Panel móvil: alertas en `/panel.html` · sync manual en Calendario / Conexión Booking.

### Base de datos en Render (importante)

**Plan free de Render:** el disco del contenedor es **efímero**. Cada redeploy o reinicio puede **borrar** `terra_natura.db` y la API vuelve a arrancar con el **seed** (unidades + reglas, sin tus reservas manuales ni sync Booking previo).

**Proyecto Don Bosco / fútbol:** no usa Render free para producción. Corre en una **VM Oracle** con archivos en disco fijo (`/opt/gestion-partidos/`). Ahí la SQLite **sí persiste** entre actualizaciones de código.

**Opciones para Terra Natura (cuando haya reservas reales en prod):**

1. **Misma VM Oracle** que Don Bosco (recomendado si ya la tenés) — patrón `local/publicar-desde-config.ps1`.
2. **Render + disco persistente** (plan de pago, montar volumen en `/app/data`).
3. **PostgreSQL** (Neon/Render/Superbase) — cambiar `DATABASE_URL`; datos sobreviven redeploys.

Hasta migrar: las reservas “oficiales” siguen en **Booking**; después de cada redeploy conviene **Sincronizar Booking** en el panel para reimportar iCal.

### Subir tu base local (tarifas reales del panel)

En Render → Shell, o copiá `terra_natura.db` al disco persistente si activás disco de pago.  
Sin eso, la API arranca con **seed** (mismas reglas de temporada/inflación que el motor).

## Opción B — Cloudflare Tunnel (tu PC o VM siempre encendida)

1. Instalá [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/).
2. En Cloudflare DNS: `api.alpinasterranatura.com.ar` → túnel a `localhost:8000`.
3. `site-config.json`: `"apiBase": "https://api.alpinasterranatura.com.ar"`
4. Dejá corriendo `local/inicia_servidor_interno.bat` + el túnel.

## Respaldo en el sitio (sin API)

Si la API no responde, la web usa `assets/data/tarifas-cotizador-cache.json` (precios del motor, sin disponibilidad Booking).

Regenerar cache:

```powershell
python scripts/build_tarifas_web_cache.py
powershell -ExecutionPolicy Bypass -File scripts\publicar-sitio-gh-pages.ps1
```

## Verificación

Caso de prueba: Alpina 1, check-in **28/05/2026**, check-out **30/05/2026** (2 noches).  
El motor local da ~**$231.700** (temporada baja + inflación), no $240.000 fijos.
