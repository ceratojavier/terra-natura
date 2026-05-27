# Decisión estratégica — Suite 4 (planta baja) vs solo Suite 5

**Situación actual**
- **Suite 4** = loft planta baja (entrada independiente, ventilador, sin A/A).
- **Suite 5** = loft planta alta (entrada independiente, A/A).
- Mismo dúplex, unidades separadas hoy.

**Idea en evaluación:** dejar de alquilar Suite 4 y convertirla en **salón de desayuno / comedor liviano** para huéspedes; alquilar solo Suite 5 arriba.

**Preocupación:** si abajo hay conversación, desayunos o cocina, ¿molesta a quien duerme en Suite 5?

---

## Recomendación resumida

| Escenario | Recomendación |
|-----------|----------------|
| **Verano / fines de semana con alta ocupación** | Mantener **Suite 4 alquilable** (ingreso $85–90k/noche) salvo que confirmen poco uso. |
| **Valor diferencial “dueños en el predio”** | **Salón PB solo desayuno** puede sumar mucho a reseñas de **Alpinas 1–3**, sin competir con Suite 5 si se regula bien. |
| **Si Suite 5 está siempre alquilada y PB es salón** | Riesgo de ruido **real pero manejable** con horario y reglas — no es automáticamente inviable. |
| **Si Suite 4 como salón Y Suite 5 vacía mucho** | El salón abajo **no genera quejas** (nadie duerme arriba). |

**Opción que suele funcionar mejor en complejos chicos:** **modelo híbrido** (ver §3), no “todo o nada”.

---

## 1. Ruido: ¿molestará a Suite 5?

Factores en tu favor:
- Uso como **desayuno 8:00–10:30** (alineado con check-out 10:00) — no fiestas nocturnas.
- Comidas **livianas** (mate, tostadas, fruta) — menos olor y ruido que cena con grupos.
- Vosotros en el predio → controláis volumen y duración.

Factores de riesgo:
- Dúplex suele tener **poca insonorización** entre PB y PA (pisos de madera, vigas).
- Si Suite 5 está ocupada y abajo hay **niños o grupo charlando** a la hora de siesta (14–17 h), puede haber reclamo.
- Cocina activa abajo = olores arriba.

**Mitigación sin obra (costo $0):**
- Cartel: *“Salón desayuno 8:00–10:30 · silencio después”*.
- No usar PB como salón de **cena** ni eventos.
- **No alquilar Suite 5 el mismo finde** que uséis PB como salón intenso para un evento del complejo (bloqueo en PMS).
- Alfombras / cortinas gruesas en PB si ya las hay (absorción sonido).
- Ofrecer desayuno en **pergola** de cada alpina como alternativa (menos gente abajo del dúplex).

**Si un día hacéis obra barata:** placa acústica en techo PB o sellado escalera — solo si el modelo salón se confirma permanente.

---

## 2. Economía: ¿conviene dejar de alquilar Suite 4?

| Mantener Suite 4 alquilable | Convertir Suite 4 en salón |
|-----------------------------|----------------------------|
| +$85–90k/noche en temporada | −1 unidad en Booking/Airbnb |
| 5 unidades = más calendario lleno | Mejor experiencia → mejor reseña y repetición en **Alpinas** |
| Menos logística (no servir desayuno) | Podéis cobrar **desayuno opcional** o subir $5–10k/noche en alpinas “con desayuno en salón” |
| Suite 5 y 4 a veces compiten (mismo perfil pareja) | Suite 5 única “loft del complejo” = más clara en marketing |

**Cálculo orientativo:** si Suite 4 se alquila **menos de ~40 noches/año** o a precio muy bajo, el salón desayuno + ligero aumento en 3 alpinas puede compensar. Si se alquila **bien todo el verano**, perder ingreso duele.

---

## 3. Tres modelos posibles (elegir uno)

### A) Status quo — las 5 unidades alquilables ✅ (default PMS hoy)
- Suite 4 y 5 independientes.
- Desayuno en pergola / barra de cada unidad (sin salón común).

### B) Híbrido ⭐ (recomendado para probar)
- **Suite 5** siempre alquilable.
- **Suite 4:** alquilable **solo cuando Suite 5 está vacía** (PMS: regla “no doble uso conflicto”).
- Cuando **Suite 5 ocupada** → Suite 4 **cerrada a reservas** y solo uso como salón 8:00–10:30 (opcional, avisando al huésped de arriba: *“abajo hay salón desayuno hasta 10:30”*).
- Ventaja: ingreso cuando podéis; menos conflicto cuando hay alguien arriba.

### C) Suite 4 solo salón permanente
- Inventario = **4 unidades** (Alpina 1–3 + Suite 5).
- Marketing: *“Desayuno en salón del complejo”* / *“Único loft con vista — Suite 5”*.
- Subir precio alpina $5k o pack desayuno $X por persona.

---

## 4. Qué haría en vuestro lugar (Terra Natura)

1. **Temporada próxima:** modelo **B (híbrido)** 2–3 meses — medir quejas Suite 5 y ocupación Suite 4.
2. **Reglas:** salón solo **8:00–10:30**; sin cenas; aviso en confirmación si Suite 5 ocupada.
3. Si **cero quejas** y las alpinas suben reseñas → evaluar modelo **C** para 2027.
4. Si **Suite 4 llena seguido** en verano → quedarse en **A** o B solo en baja.

---

## 5. Para el sistema (cuando decidan)

| Decisión | Cambio PMS |
|----------|------------|
| A | Sin cambios |
| B | Flag `suite4_modo`: `alquiler` \| `salon` según ocupación `suite-5` |
| C | `suite-4` → tipo `espacio_comun`; quitar de OTAs; 4 unidades en channel manager |

**Dueño — marcar decisión:** [ ] A  [ ] B  [ ] C  [ ] Probar B hasta fecha: ______
