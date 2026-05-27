# Tarifas, promos y equivalencias — Terra Natura

Referencia oficial de negocio: `docs/REGLAS_NEGOCIO.md`.  
Este archivo explica **cómo calcula el motor** equivalencias por noche y descuentos.

---

## Variables

| Símbolo | Significado |
|---------|-------------|
| `V` | Precio noches verano orientativo por unidad (ej. alpina `$110–120k`, suite `$85–90k`) |
| `B_finde` | Precio noches **fin de semana** en **temporada baja** (respecto de verano: definir `%` por tipo en configuración PMS — ej. 70 %) |
| `B_sem` | Precio noches **lunes a jueves** en baja: **`B_sem = B_finde × 0.85`** (−15 % respecto del unitario de finde en baja) |

> El **−15 % en semana dentro de temporada baja** se aplica **sobre el precio ya bajado** de finde en esa temporada (`B_finde`), no sobre verano directo.

---

## Promos en temporada baja (respecto del precio baja vigente esa noche)

Se aplican sobre el total de noches cobradas; el huésped paga noches gratis.

### Promo **3 × 2** (3 noches, pagás 2)

Sea `P_i` el precio de cada noche `i` (puede ser mezcla `B_sem` / `B_finde`).

Sin mezclas (todas iguales a `P`):  
Total a cobrar \(= 2P\). Duración \(= 3\) noches.

\[
\text{Equivalente por noche} = \frac{2P}{3} \approx 0{,}667\,P \quad (\approx 33{,}3\%\ \text{dto medio por noche})
\]

Ejemplo alpina si `P = B_sem = $70.000`: total **$140.000** por 3 noches → **$46.667/noche** efectivo.

### Promo **4 × 3** (4 noches, pagás 3)

\[
\text{Equivalente por noche} = \frac{3P}{4} = 0{,}75\,P \quad (25\%\ \text{dto medio por noche})
\]

Ejemplo `P = $70.000`: pagás **$210.000** por 4 noches → **$52.500/noche** efectivo.

### Mezcla finde + semana

El PMS debe:  
1. Marcar noches vie–sáb como `B_finde`, lun–jue como `B_sem`.  
2. Agrupar el paquete 3×2 o 4×3 sobre el **subtotal** de las noches “pagadas” según política definida del complejo:

**Política recomendada:** las noches gratuitas aplican sobre las noches **más baratas** del período primero.

---

## Reserva **directa** vs **Booking.com**

Precio cargado para que después de **comisión** quede cercano al directo:

\[
\text{Precio público Booking} \approx \text{Precio directo} \times (1 + 0{,}18) = \text{Directo} \times 1{,}18
\]

Ej.: directo alpina `$120.000` → publicar Booking ≈ **`$141.600`/noche** (18 % markup).

> La comisión real de Booking puede variar por contrato; el **18 %** es el parámetro del dueño. Ajustalo en configuración cuando el dashboard te muestre el neto real.

---

## Descuento **10 % pagó en efectivo**

Sobre el **total de la estadía** (tras promos aplicadas), si todo el saldo pendiente lo abona en **efectivo** según política vigente:

\[
\text{Total final} = \text{Total} \times 0{,}90 \quad (\text{−10\%})
\]

No debe combinarse dos veces con descuentos no permitidos por reglas internas — el `pricing_engine` lo validará.

---

## Resumen visual (misma tarifa nominal `P` por todas las noches del paquete)

| Promo | Pagás noches | Quedás noches | Total / precio noches “regaladas” | Equiv. sobre `P` |
|-------|---------------|---------------|------------------------------------|-------------------|
| 3×2 | 2 | 3 | \(2P/3\) por noche | **−33,3 % medio** |
| 4×3 | 3 | 4 | \(3P/4\) por noche | **−25 % medio** |
| Lun–jue en baja | — | sobre `B_finde` | `B_sem = 0,85 × B_finde` | **−15 %** vs finde baja |

---

## Próximo paso en código

Implementar en `backend/services/pricing_engine.py`:  
entrada `{ fechas[], unidad_id, modo_pago?, canal?, promo_codigo? }` → línea por noche + totales + texto legal para voucher.
