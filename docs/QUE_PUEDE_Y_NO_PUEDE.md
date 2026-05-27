# Terra Natura — Qué puede y qué NO puede el sistema (honesto)

Para el dueño: sin promesas de marketing vacías.

---

## Dónde está cada cosa (no se borró)

| Qué querés | URL / archivo |
|------------|----------------|
| **Programa** (YouTube, videos, calendario editorial) | Icono escritorio → `http://127.0.0.1:8000/programa` |
| **Marketing** (textos, calendario posts, WhatsApp) | `http://127.0.0.1:8000/marketing` — **no lo tocamos** |
| **Panel reservas** | `http://127.0.0.1:8000/panel` |
| **Turismo / grilla** | `http://127.0.0.1:8000/turismo` |
| **Agentes** | `http://127.0.0.1:8000/agentes` |
| Fotos del complejo | `archivos multimedia/fotos terra natura/` |
| Eventos con fecha real | `ama/data/eventos_confirmados_ar.json` |

El calendario blanco de publicaciones **ya no es la pantalla principal**. Volvió el programa verde oscuro; la agenda está **plegada abajo** (“Agenda de eventos confirmados”).

---

## Qué SÍ puede hacer hoy

1. **Recolectar videos YouTube** (B-roll Punilla) si tenés `YOUTUBE_API_KEY` en `.env`.
2. **Generar calendario editorial** de posts borrador (texto + fechas) para un rango.
3. **Armar videos** con fotos de `archivos multimedia` + B-roll (necesita ffmpeg).
4. **Listar feriados y puentes** oficiales Argentina (JSON).
5. **Mostrar fiestas con fecha confirmada** que están en `eventos_confirmados_ar.json` (Cosquín, Avicultura, Kempes, Feria Córdoba, etc.).
6. **Sugerir copy** para Instagram/WhatsApp desde plantillas (ángulo Bialet).
7. **Usar fotos del complejo** (parque, pileta, cabañas) en posts cuando no hay foto del festival.
8. **Intentar bajar** una foto del evento desde web (página oficial / Wikimedia) al actualizar agenda — **solo si hay imagen pública** y con internet.

---

## Qué NO puede hacer (limitaciones reales)

1. **No inventar recitales** ni fechas que no estén en el JSON confirmado o feriados oficiales.
2. **No publicar solo en Instagram/Facebook** todavía (falta conectar API Meta; hoy copiás y pegás).
3. **No leer WhatsApp entrante** automático (sin API WhatsApp Business conectada).
4. **No garantizar foto** de cada festival: muchas webs no tienen imagen libre o el link está roto.
5. **No reemplazar** al channel manager de Booking/Airbnb (MVP es iCal manual).
6. **No cobrar** Mercado Pago ni confirmar reservas sin que el PMS esté terminado y probado.
7. **No saber** precios finales si no están cargados en reglas de negocio / motor de precios.

---

## Por qué veías “eventos ficticios”

Había un **error de código**: todo lo que venía del scraper **sin estado** se marcaba como “confirmado”. Eso mezclaba títulos de internet sin fecha con fiestas reales.

**Corregido:** solo entra si `estado: confirmado` explícito, o feriado/puente oficial. El cache web **no se mezcla** cuando pedís solo confirmados.

La lista real de fiestas está en `ama/data/eventos_confirmados_ar.json` (~19 eventos con fechas). No son cientos: **es a propósito**.

---

## Qué hacer AHORA (3 pasos)

1. **Cerrá** la ventana negra del servidor si está abierta.
2. **Abrí de nuevo** el icono **Terra Natura** del escritorio (o `local\Abrir-Terra-Natura.bat`).
3. En el navegador:
   - Usá el programa como antes: botones **1 · YouTube**, **2 · Calendario editorial**, **3 · Videos**.
   - Si querés ver fiestas: abrí el desplegable **“Agenda de eventos confirmados”** → **Ver eventos confirmados**.

**Ctrl+F5** en el navegador para refrescar sin caché vieja.

---

## Si querés agregar un evento real

Decile al agente (o editá el JSON) con **fecha oficial** y link de la municipalidad / productora. Ejemplo:

- Nombre, `fecha_inicio`, `fecha_fin`, `localidad`, `fuente_url`, `estado: confirmado`

Sin eso **no aparece** (y está bien).

---

## Resumen en una frase

**El programa de siempre sigue en `/programa` y `/marketing`; el calendario blanco quedó opcional y acotado a fechas reales — no rellena el mes con inventos.**
