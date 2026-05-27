# Campañas Instagram / Meta y landings — Terra Natura

## ¿La campaña tiene que ir a una landing o a la home?

**En la mayoría de los casos: a una landing.** La home sirve para SEO y para quien ya conoce la marca. El anuncio en Instagram es interrupción: tenés **3 segundos** para mostrar *una* promesa (parejas, familia, reserva directa, evento en Punilla). Si mandás a la home, el usuario se pierde entre secciones y baja la conversión.

| Objetivo del post / anuncio | URL recomendada (cuando el dominio esté en producción) |
|------------------------------|--------------------------------------------------------|
| Escapada romántica / suites | `/landings/parejas` |
| Familia, pileta, niños | `/landings/familia` |
| “Escribinos y ahorrá vs OTA” | `/landings/reserva-directa` |
| Evento, puente, Cosquín, valle | `/landings/punilla` |
| Marca general / Google orgánico | `/` (home) |

**UTM sugeridos** (Medición en Analytics / Meta):

- `utm_source=instagram`
- `utm_medium=paid` o `social` (orgánico)
- `utm_campaign=parejas_abril` (cambiar por mes u oferta)
- `utm_content=carrusel_pileta` (opcional, variante creativo)

Ejemplo: `https://TU-DOMINIO.com/landings/parejas?utm_source=instagram&utm_medium=paid&utm_campaign=verano26`

El sitio ya incluye `assets/js/utm.js` que guarda UTMs en `sessionStorage` para futuro CRM o mensaje prearmado en WhatsApp.

---

## Ideas extra (gerencia marketing + operación baja)

1. **Anuncio “últimas 2 unidades finde”** → landing `punilla` o `parejas` + mensaje WhatsApp prellenado con fecha.
2. **Carrusel antes/después amanecer valle** → `parejas` + CTA “Pedir balcony view”.
3. **Reels pileta 10–20 h** → `familia` con recordatorio de horario pileta (confianza).
4. **Estado / historia** con link `reserva-directa` en temporada media (menos comisión que Booking).
5. **Remarketing** (cuando tengas pixel): quien vio Booking pero no reservó → anuncio `reserva-directa`.
6. **WhatsApp listas** (difusión): mismo link landing que organic para no romper métricas.
7. **Google Ads local** mismo esquema: anuncio “cabaña pileta Bialet” → home o `punilla`.

---

## Desarrollo futuro cercano

- Formulario corto nombre + fecha + unidad preferida (lead) antes del salto a WhatsApp.
- Página `/landings/promo-nombre-del-evento.html` cuando AMA detecte Cosquín Rock / Kempes etc.
- `robots.txt` y `sitemap.xml` cuando el dominio esté público.
