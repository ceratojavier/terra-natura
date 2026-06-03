# Estrategia comercial 2026 — ocupación y rentabilidad

**Fuente:** estrategia comercial del dueño (jun 2026) · complementa `docs/CALENDARIO_COMERCIAL_2026.md`

Objetivos: más **noches por reserva**, menos **huecos**, sin **destruir tarifa** ni parecer desesperados.

---

## Regla principal

| Demanda | Qué hacer | Qué evitar |
|---------|-----------|------------|
| **Alta** | Urgencia suave, escasez, beneficios baratos, check-out extendido | Descuentos agresivos |
| **Media** | Promos de estadía, regalos regionales, valor percibido | Rebajas grandes |
| **Baja** | Promos fuertes que sumen **noches** (4→5, 2+1 efemérides) | Regalar plata sin estadía |

**Meta 2026:** estadía promedio de **2 → 3–5 noches** (ahí está la rentabilidad).

---

## Por fecha importante

### Carnaval · Semana Santa · Octubre · Noviembre

- **NO** descuento agresivo.
- Mensaje: reservar con anticipación, pocas unidades.
- Beneficio: check-out extendido / detalle bienvenida (costo bajo).

### Mayo (mes flojo)

- Vender **escapada romántica** y **descanso**, no “cabaña”.
- 2 noches + detalle regional (vino chico, alfajores, desayuno seco).

### Junio (inicio invierno)

- Empujar **3 noches** en finde Bandera (22 jun): no quedarse en finde corto de 2.
- Beneficio: salida tarde, obsequio regional, upgrade si hay lugar.

### Vacaciones invierno (julio)

- Objetivo: **más días**, no solo llenar.
- Promo **5+1** con frase *«mientras más descansás, más te conviene»*.
- **BA/CABA:** campaña **45 días antes**. Córdoba **20–25 días**. Santa Fe / Entre Ríos **30 días**.

### Lunes a sábado AM (temporada baja)

- **Pagás 4, te quedás 5** — vender **tiempo**, no precio.
- Segmentos: parejas, jubilados, home office, familias.

---

## Huecos entre reservas

Ej.: sale miércoles, entra sábado → **3 noches hueco**.

- No bajar precio desesperado.
- **Promo último momento** con beneficio de estadía (no gritar “descuento”).
- Descuento real **solo** si faltan **<72 h** y está vacío: **5–10 % máximo**, nunca 20–30 %.

---

## Ventas WhatsApp

### Nunca solo precio

Mal: *«Sale $120.000.»*  
Bien: disponibilidad + valor (pileta, parque, vista, Bialet, cerca del lago) + precio + pregunta fechas/personas.

### Urgencia sin desesperación

- *«Las fechas largas suelen ocuparse con anticipación.»*
- *«Te recomiendo consultar apenas definan fecha.»*

### Objetivo oculto de la IA

Cerrar reserva · más noches · seña · valor antes que descuento.

---

## Integración en el proyecto

| Módulo | Uso |
|--------|-----|
| `ama/engine/comercial_2026.py` | Promo/tarifa/estrategia por fecha |
| `ama/engine/plan_marketing_unificado.py` | Copy de campañas |
| `ama/chat/responder.py` | Reglas + escalado (LLM opcional con prompt maestro) |
| `backend/services/pricing_engine.py` | Alinear config tarifas con tabla 2026 |
| AMA modo 🟡 | Publicar solo con aprobación dueño |

Ver también `docs/WHATSAPP_IA_PROMPT_MAESTRO.md` y `docs/BIBLIOTECA_MENSAJES_WHATSAPP.md`.
