# Calendario turístico comercial 2026 — Terra Natura

**Fuente:** calendario y tarifas definidos por el dueño (correo jun 2026).  
**Datos máquina:** `ama/data/calendario_comercial_2026.json` · **Motor:** `ama/engine/comercial_2026.py`

Pensado para **ocupación real** en Bialet Massé / sierras de Córdoba (mercado Carlos Paz, Buenos Aires, Córdoba, Santa Fe, Entre Ríos). No usar solo el feriado del calendario oficial: importa **cómo viaja la gente**.

---

## Regla de finde largo (Argentina)

| Feriado | Ingreso típico | Noches hospedadas | Retiro | Resultado |
|---------|----------------|-------------------|--------|-----------|
| **Lunes** | Viernes post trabajo | Vie · Sáb · Dom | Lunes | **3 noches** |
| **Viernes** | Jueves tarde/noche | Jue · Vie · Sáb | Domingo | **3 noches** |
| **Puente turístico** | Según decreto | — | — | **4 noches** |
| **Mar / Mié / Jue sin puente** | — | — | — | **No** es finde largo principal (movimiento secundario) |

Los agentes deben cruzar esto con `ama/data/feriados_puentes_ar.json` y `marketing/contexto/calendario_reglas.md`.

---

## Temporadas 2026

### Alta — precio pleno, sin descuentos fuertes

Enero · Carnaval · Semana Santa · Vacaciones invierno · Octubre · Noviembre (puente) · Diciembre (parcial) · findes largos.

| Unidad | Tarifa/noche |
|--------|----------------|
| Alpina (4/5 pers.) | **$120.000** |
| Suite (2/3 pers.) | **$100.000** |

### Media — beneficios, no rebajas grandes

Marzo · Abril (fuera Semana Santa) · Agosto · Septiembre.

Estrategia: check-out extendido, detalle de bienvenida, promo por estadía.

### Baja — llenar ocupación

Mayo · Junio (parcial) · semanas flojas de noviembre.

| Unidad | Tarifa/noche |
|--------|----------------|
| Alpina | **$100.000** |
| Suite | **$85.000** |

---

## Findes largos reales 2026

| Evento | Fechas clave | Ingreso | Noches objetivo | Potencial | Promo (no descontar si dice NO) |
|--------|--------------|---------|-----------------|-----------|----------------------------------|
| **Carnaval** | 14–17 feb | Vie 13 | **4** | ★★★★★ | 4 noches + check-out extendido |
| **Semana Santa** | 2–5 abr | Jue 2 | **3** | ★★★★★ | Late check-out 3+ noches |
| **1° Mayo** | 1–3 may | Jue 30 abr | **3** | ★★★★☆ | Detalle bienvenida regional |
| **25 Mayo** | Lun 25 | Vie 22 | **3** | ★★★★☆ | 3 noches + beneficio anticipada |
| **Bandera (jun)** | Lun 22 jun | Vie 19 | **3** | ★★★★☆ | Escapada invierno 3 noches |
| **San Martín (ago)** | Lun 17 ago | Vie 14 | **3** | ★★★☆☆ | Escapada serrana invierno |
| **12 Oct** | Lun 12 oct | Vie 9 | **3** | ★★★★★ | Urgencia, últimas cabañas |
| **Soberanía + puente** | Vie 20 nov | Jue 19 | **4** | ★★★★★ | 4 noches + beneficio anticipada |

---

## Vacaciones de invierno 2026 — ventana ~3 semanas

No vender una sola fecha: vender **ventana continua** (aprox. **6 al 31 jul 2026**).

| Ola | Fechas est. | Mercado | Campaña |
|-----|-------------|---------|---------|
| 1 temprana | 6–17 jul | Córdoba, Mendoza, Neuquén, etc. | Fuerte invierno |
| 2 gran ola | 13–24 jul | **Buenos Aires, CABA** | **Máxima presión** — arrancar **45 días antes** |
| 3 | 13–24 jul | Santa Fe, Entre Ríos | **30 días antes** |
| 4 tardía | 20–31 jul | Norte/sur | Estirar ocupación |

### Promo oficial invierno

**Te hospedás 5 noches y la 6.ª es bonificada** (Alpina y Suite).  
Tarifas invierno: Alpina **$120.000** · Suite **$100.000**.  
**No bajar precios** en julio. Frase: *«Mientras más descansás, más te conviene»* (no *«te regalo una noche»*).

---

## Efemérides Terra Natura

- **Día del Padre / Madre / Niño:** 2 noches + 1 gratis.

## Promo fija temporada baja

**Pagás 4 noches y te quedás 5** — lunes a sábado por la mañana.  
Ideal: parejas, home office, familias chicas.

---

## Copy y marca

- Copy **público** (IG, web, ads): ver `docs/COPY_TONO_MARCA.md` — **no** “Punilla” como gancho principal; sí **sierras**, **Bialet**, **lago San Roque**.
- WhatsApp comercial puede mencionar Carlos Paz y recorridos; biblioteca adaptada en `docs/BIBLIOTECA_MENSAJES_WHATSAPP.md`.

---

## Referencias

- Estrategia detallada: `docs/ESTRATEGIA_COMERCIAL_2026.md`
- Prompt IA WhatsApp: `docs/WHATSAPP_IA_PROMPT_MAESTRO.md`
- Tarifas motor PMS: `docs/TARIFAS_PROMOCIONES.md` · `docs/REGLAS_NEGOCIO.md`
