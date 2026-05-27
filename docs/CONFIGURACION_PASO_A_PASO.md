# Configuración paso a paso — Terra Natura

Como en **Jurídico**: un paso, lo probamos, queda funcionando, y recién ahí el siguiente.  
**No hace falta programar.** Si algo no entendés, anotá en qué paso quedaste.

---

## Cómo venimos (resumen)

| Bloque | Estado |
|--------|--------|
| Documentación del negocio (unidades, tarifas, reglas) | ✅ Lista |
| Programa en tu PC (servidor + web + panel) | ✅ Armado |
| Acceso directo escritorio «Terra Natura - Entrada» | ✅ Creado (si no lo ves, ver Paso 0) |
| Cotizar fechas en la web | ✅ Funciona si el servidor está encendido |
| Reservas en base + ver en panel | ✅ Funciona (API; panel lectura) |
| Exportar calendario a Airbnb/Booking (iCal) | ✅ Enlaces en panel → Calendarios |
| Importar bloqueos desde Airbnb/Booking | ⬜ Paso 4 (después) |
| Consultas web → te avisa en panel + texto para WhatsApp | ⬜ Paso 3 (próximo desarrollo) |
| WhatsApp automático (API Meta) | ⬜ Paso 6 (opcional; tiene costo posible) |
| Publicar en Instagram/Facebook solo | ⬜ Paso 7 (cuentas Meta) |

---

## Paso 0 — Que el programa abra en tu PC

**Objetivo:** Doble clic en el escritorio → se abre el navegador con el panel.

**Qué hacés vos:**
1. Buscá en el escritorio **«Terra Natura - Entrada»**.
2. Doble clic.
3. Debe abrirse el navegador en una página verde con iconos grandes.
4. Si aparece una ventana negra «servidor», **dejala abierta** mientras usás el sistema.

**Si no está el ícono** (una sola vez, con ayuda de alguien con PC):
```powershell
powershell -ExecutionPolicy Bypass -File ".\local\Crear-acceso-escritorio.ps1"
```
(desde la carpeta del proyecto)

**Listo cuando:** entrás al panel sin error de “no se pudo conectar”.

**Qué me decís:** «Paso 0 OK» o qué mensaje de error ves.

---

## Paso 1 — Probar una cotización (como un cliente)

**Objetivo:** Ver que precios y disponibilidad salen del sistema.

**Qué hacés vos:**
1. En el panel, tocá **Cotizar** (o en la web pública, sección cotización).
2. Elegí unidad, fechas de entrada y salida, tocá **Cotizar ahora**.
3. Debe mostrar un monto en pesos y si hay lugar o no.

**Listo cuando:** ves un total en ARS y un botón a WhatsApp.

**Qué me decís:** «Paso 1 OK» o captura del error.

**No te pido:** nombre del complejo, WhatsApp, dirección (ya están cargados).

---

## Paso 2 — Una reserva de prueba (solo para vos)

**Objetivo:** Que el calendario interno guarde una estadía ficticia.

**Qué hacés vos:** Por ahora esto lo cargamos **desde el panel/API** en una mejora próxima (formulario «Nueva reserva» en panel).  
**Hasta que exista el botón:** el Paso 2 lo hace quien te ayuda con la PC una vez, o lo saltamos y seguimos al Paso 3.

**Listo cuando:** en panel → **Reservas** aparece al menos una fila de prueba.

**Qué me decís:** «Paso 2 OK» o «saltamos al 3».

---

## Paso 3 — Consultas desde la web (sin API WhatsApp) — *próximo a programar*

**Objetivo:** Cliente deja consulta en la web → vos la ves en el panel → el sistema te sugiere texto → vos pegás en WhatsApp.

**Qué hacés vos:** Nada todavía; es desarrollo.

**Qué necesito de vos para cuando lo programemos:** Solo confirmar que querés este flujo (sí/no).

**Listo cuando:** en el panel hay lista «Consultas nuevas» y botón «Copiar para WhatsApp».

---

## Paso 4 — Calendarios en Airbnb / Booking (gratis, iCal)

**Objetivo:** Que las OTAs vean fechas ocupadas cuando vos reservás en el PMS.

**Qué hacés vos:**
1. Panel → **Calendarios**.
2. Por cada unidad, **Copiar enlace**.
3. En Airbnb o Booking, donde diga «importar calendario» / «sincronizar», pegás ese enlace.

**Qué me podés pasar (solo si tenés):** enlaces públicos de tus **listings de Airbnb** (uno por unidad), para guardarlos en config. **No** hace falta contraseña de Airbnb acá.

**Listo cuando:** pegaste al menos un enlace en una OTA y no te da error.

**Qué me decís:** «Paso 4 OK en Alpina 1» (o qué unidad).

---

## Paso 5 — Fotos y textos del sitio (cuando quieras pulir)

**Objetivo:** Web más linda con fotos reales.

**Qué hacés vos:** Fotos en `archivos multimedia/` según `docs/MEDIA_INVENTARIO.md` (sin ñ en nombres de archivo).

**No bloquea** los pasos 0–4.

---

## Paso 6 — WhatsApp API Meta (opcional, después)

**Objetivo:** Mensajes entran al sistema y sugerencias automáticas.

**Qué hacés vos:** Registro en developers.facebook.com (guía en conversación previa).

**Qué necesitás después:** URL pública del servidor + tokens en `.env` (no en el chat).

**Costo:** registro gratis; conversaciones pueden tener costo según Meta.

---

## Paso 7 — Redes (Instagram / Facebook) — después

**Objetivo:** Borradores de posts y publicar con aprobación.

**Qué hacés vos:** Instagram Business + página Facebook vinculadas.

---

## Regla de trabajo (como Jurídico)

1. Hacemos **un solo paso**.
2. Vos probás y me decís **OK** o el error.
3. Recién ahí pasamos al siguiente.
4. **No** repetimos datos que ya están en `docs/REGLAS_NEGOCIO.md` y en el programa.

---

## Paso actual recomendado

**→ Paso 0 y Paso 1** (abrir el programa y cotizar una vez).

Cuando me confirmes, seguimos con **Paso 4** (iCal) o programamos **Paso 3** (consultas web + sugerencia WhatsApp manual).
