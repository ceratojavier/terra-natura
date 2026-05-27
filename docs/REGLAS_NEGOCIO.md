# Reglas de negocio — Cabañas Alpinas Terra Natura

**Nombre comercial:** Cabañas Alpinas Terra Natura  
**Dirección:** Los Talas 759, Bialet Massé, Córdoba, Argentina  
**Predio:** ~2.000 m² — **un solo complejo cerrado** que incluye:
- Las **5 unidades en alquiler** (3 alpinas + 2 lofts)
- La **casa de los dueños**, dentro del mismo predio (no se alquila, no aparece en calendario ni OTAs)
- **Áreas comunes:** parque, pileta, solarium, casita niños, circulación y estacionamiento

> Los huéspedes comparten el predio con los anfitriones que **viven allí**. Es un diferencial de atención personalizada, no un “complejo solo para turistas”.

---

## Casa de los dueños (dentro del complejo)

| Aspecto | Regla para el sistema y la comunicación |
|---------|----------------------------------------|
| **En PMS / calendario** | No es unidad alquilable; excluida de disponibilidad, precios y channel manager |
| **En mapa / QR / web** | Opcional: indicar “anfitriones en el predio” sin detallar domicilio privado |
| **Check-in** | Recepción presencial o coordinada por WhatsApp con quien vive en el complejo |
| **Urgencias** | Contacto directo con anfitriones (mismo predio) |
| **Privacidad** | Respeto de la vivienda familiar; huéspedes no deben ingresar a la casa de dueños |
| **Marketing** | Mensaje: *“Atención de los dueños en el lugar — te recibimos en el complejo”* |
| **Ruido / convivencia** | Mismas reglas de respeto que en barrio de quintas; silencio nocturno aplica a todo el predio |

El AMA y las plantillas WhatsApp deben usar tono de **anfitrión presente en el complejo**, no “oficina externa”.

---

## Ubicación y entorno (copy oficial)

- A **600 m** del **Lago San Roque**, del **Arroyo Las Mojarras** y de la **nueva rotonda de la Autovía del Valle de Punilla** — acceso cómodo para recorrer la región.
- Barrio de **casas quintas y cabañas**, entorno tranquilo y natural.
- **Centro de Bialet Massé:** ~2 km.
- **Balneario Las Barrancas Bermejas** (río Cosquín): ~2 km.

**SEO / palabras clave:** cabañas Bialet Massé, alojamiento Valle de Punilla, cerca Dique San Roque, cabañas con pileta Córdoba.

---

## Contacto (datos públicos)

| Canal | Dato |
|-------|------|
| **WhatsApp reservas** | [+54 9 3541 571190](https://wa.me/5493541571190) — enlace directo reservas |
| **Email** | terranaturaalpinas@gmail.com |
| **Booking (público huéspedes)** | [Cabañas Alpinas Terra Natura en Booking](https://www.booking.com/hotel/ar/cabanas-alpinas-terra-natura-bialet-masse.es.html) *(URL limpia sin parámetros largos)* |
| **Google Maps / Business** | Buscador: *«Cabañas Alpinas Terra Natura Bialet Massé»* — perfil de negocio en Google |
| **Facebook / Instagram** | URLs cuando existan (para web y redes) |

> **Administración extranet Booking / cuentas Gmail / Google Business:** no se documentan aquí. Credenciales únicamente `.env` local o gestor de secretos; ver `docs/SEGURIDAD_CREDENCIALES.md`.

**Recargo publicado en Booking sobre precio directo (neto alojamiento):** cargar en la extranet aprox. **+18 %** sobre la tarifa que cobrás en reserva directa, para compensar comisión aproximada de la plataforma. El PMS guarda el parámetro en `config_tarifas.booking_markup_sobre_precio_directo` (= 0.18). Ajustar si el informe de Booking muestra otro neto.

Otros canales y prioridades: `docs/CANALES_VISIBILITY_ARGENTINA.md` · Airbnb cuando tengas cuenta: `docs/AIRBNB_CHECKLIST.md`.

---

## Inventario — 5 unidades de alquiler

**Nomenclatura oficial (confirmada por dueños):**

| ID sistema | Nombre comercial | Slug | Tipo |
|------------|------------------|------|------|
| `alpina-1` | **Alpina 1** | `alpina-1` | Cabaña alpina 2 plantas |
| `alpina-2` | **Alpina 2** | `alpina-2` | Cabaña alpina 2 plantas |
| `alpina-3` | **Alpina 3** | `alpina-3` | Cabaña alpina 2 plantas |
| `suite-4` | **Suite 4** | `suite-4` | Loft **planta baja** del dúplex (sin A/A, ventilador) — **confirmado** |
| `suite-5` | **Suite 5** | `suite-5` | Loft **planta alta** del dúplex (con A/A) — **confirmado** |

| ID | Capacidad máx. | Posicionamiento venta |
|----|----------------|----------------------|
| Alpinas 1–3 | 4 (2 adultos + 2 menores) | **Súper cómoda para 2** · familia con chicos |
| Suite 4–5 | 3 (2 + 1) | Pareja · “cabaña pequeña” · Suite 4 sin escaleras |

> Ficha técnica: `docs/UNIDADES.md` · Ideas marketing: `docs/MARKETING_IDEAS.md`

### Configuración en software (PMS)

Todas las opciones abajo son editables sin código: ver **`docs/CONFIGURACION_PMS.md`** y API `/api/config/resumen`.

- **Desayuno:** `habilitado: false` por defecto.
- **5 unidades alquilables** por defecto; cada una con `activa`, `alquilable`, `uso_modo`.
- **Suite 4 / 5:** regla `suite4_reglas.modo = independiente` (cambiable a `hibrido` o `solo_salon`).

### En evaluación: ¿Suite 4 solo como salón / desayuno?

**Consulta dueños:** dejar de alquilar Suite 4 (PB) y usarla como **saloncito de desayuno** o comidas livianas; alquilar solo Suite 5 (PA). Preocupación: **ruido** hacia huéspedes de arriba.

**Estado PMS:** mientras no se decida, Suite 4 sigue como unidad alquilable en calendario. Si se aprueba el cambio → `suite-4` pasa a `espacio_comun` (sin iCal/OTA) y el inventario baja a **4 unidades** (3 alpinas + Suite 5).

**Análisis y recomendación:** ver `docs/DECISION_SUITE4.md`.

---

## Horarios de estadía

| Concepto | Horario |
|----------|---------|
| **Check-in** | **11:30** hs |
| **Check-out** | **10:00** hs |
| **Check-in flexible** | Sujeto a disponibilidad del día — coordinar por WhatsApp con recepción (dueños en predio) |

El PMS y los mensajes automáticos deben usar estos horarios por defecto.

---

## Reservas, seña y pagos

### Seña (confirmación de reserva)
- **Monto:** **50 %** del total de la estadía.
- **Plazo para abonar seña:** **48 horas** desde la pre-reserva (configurable en PMS).
- Si no se abona en plazo: la reserva pasa a `cancelada` y se libera el calendario en todos los canales.

### Saldo
- **50 % restante:** a abonar **antes del check-in** (mínimo 24 h antes) o **al momento del ingreso** en efectivo/transferencia/MP — [confirmar preferencia del dueño].

### Medios de pago aceptados
- Transferencia bancaria (con carga de comprobante en web/WhatsApp).
- **Mercado Pago** (link de pago automático al confirmar).
- **Efectivo** en el predio: si toda la estadía (saldo) se abona en efectivo según acuerdo, aplica **−10 % sobre el total** de la estadía (tras aplicar promos y tarifas). Configuración: `tarifas_promociones.descuento_efectivo_sobre_total` = 0.10.

### Depósito en garantía
- **No se solicita depósito en garantía.** Destacar en web y OTAs como ventaja (*“Reservá sin depósito de garantía”*).

---

## Política de cancelación (vinculada a seña del 50 %)

| Situación | Efecto |
|-----------|--------|
| **Cancelación con más de 15 días** de anticipación al check-in | Reintegro **100 %** de la seña abonada (o reprogramación sin cargo, a elección del huésped si hay disponibilidad). |
| **Cancelación entre 8 y 15 días** | Retención **50 %** de la seña (equivale al 25 % del total de la estadía). Reintegro del 50 % restante de la seña. |
| **Cancelación con 7 días o menos** | **Seña no reembolsable** (se retiene el 50 % abonado). |
| **No show** (no se presenta sin aviso) | Sin reembolso. Se retiene seña; saldo no adeudado si no ingresó. |
| **Salida anticipada** | No hay reembolso de noches no utilizadas salvo fuerza mayor documentada (criterio administración). |

**Texto corto para OTAs y web:**  
*"Se requiere seña del 50 % para confirmar. Cancelación gratuita de la seña hasta 15 días antes del ingreso. Entre 8 y 15 días: retención del 50 % de la seña. Con 7 días o menos: seña no reembolsable."*

> Si el dueño prefiere otros plazos (ej. 10 / 20 días), ajustar solo esta tabla y las plantillas automáticas.

---

## Amenities del complejo (áreas comunes)

| Servicio | Detalle |
|----------|---------|
| **Pileta** | Descubierta **6 m × 3 m**, profundidad **1,50 m** |
| **Solarium** | Reposeras junto a la pileta |
| **Parque** | ~2.000 m² — hamacas, **casita para niños** |
| **Estacionamiento** | **Techado con media sombra** (tipo hipermercado), por unidad según disponibilidad en predio |
| **Dueños en el predio** | Atención y asistencia personalizada |

Horario de pileta y reglas de uso: **10:00–20:00**. Niños siempre con adulto en el agua.

---

## Servicios incluidos en todas las unidades

- **WiFi**
- **Smart TV** con TV por internet (**Netflix, YouTube** — cuenta del huésped o modo invitado según política)
- **Ropa blanca:** sábanas, toallas, **ropa de cama de abrigo**
- **Baño completo** con ducha
- **Heladera con freezer**, cocina con **horno**
- **Pérgola privada** junto a cada cabaña: bancos, mesa y **asador**
- Estacionamiento techado en el complejo

### Diferencias entre tipos

| Característica | Alpina 1, 2, 3 | Suite 4 (PB) | Suite 5 (PA) |
|----------------|---------------------|------------------|-------------------|
| Planta baja | **6 × 5,5 m** (~33 m²) living-comedor + baño + cocina con **barra desayunadora** + 2 camas 1 plaza | Monoambiente, entrada propia | Monoambiente, entrada propia |
| Planta alta | Dormitorio matrimonial + **balcón vista panorámica Valle de Punilla** | — | — |
| Climatización PA/PB | **A/A frío-calor** en dormitorio matrimonial (alpina) | **Ventilador de techo** (sin A/A) | **A/A frío-calor** |
| Camas | Matrimonial PA + 2×1 plaza PB | Matrimonial + 1 plaza | Matrimonial + 1 plaza |
| Pérgola + parrilla | Sí (cada una) | Sí | Sí |

---

## Políticas del predio

| Tema | Regla |
|------|-------|
| **Mascotas** | **Sí, solo pequeñas** (perro/gato). **No pueden quedar solas** en la cabaña si los huéspedes salen a pasear. Informar en reserva. Cartel en unidad + texto en web/OTA. |
| **Parrilla / asador** | Uso bajo pergola de cada unidad; apagar brasas; no fuego en pasto |
| **Pileta** | Uso bajo responsabilidad del huésped; niños con adulto |
| **Ruido / fiestas** | Respeto vecinal (barrio quintas); silencio nocturno sugerido desde **23:00** |
| **Fiestas evento** | Solo con autorización previa de administración |
| **Fumar** | Solo exterior y con cuidado brasas; interior no fumar |

---

## Canales de venta y motor centralizado

**Objetivo:** Un solo **calendario maestro** en el PMS Terra Natura. Toda reserva (directa, Booking, Airbnb) bloquea inventario en tiempo real.

| Canal | Uso | Configuración |
|-------|-----|----------------|
| **Reserva directa** | Web propia + WhatsApp | Siempre activo (prioridad: sin comisión OTA) |
| **Booking.com** | OTA | Sincronización iCal / API — fotos y textos desde panel o AMA |
| **Airbnb** | OTA | Idem |

### Interruptor global en PMS (`config_canales`)

```yaml
modo_solo_reserva_directa: false   # true = OTAs pausadas, solo web/WhatsApp
booking_habilitado: true
airbnb_habilitado: true
```

- Si `modo_solo_reserva_directa: true`:
  - No exportar disponibilidad a OTAs (o cerrar calendarios en extranet).
  - Web y WhatsApp siguen operativos.
  - AMA deja de promocionar links OTA.

**Gestión de fotos:** briefs en AMA; carga en Booking con usuario **extranet oficial** (sin compartir contraseña por chat).  
**Lista pública:** [Booking — Terra Natura Bialet Massé](https://www.booking.com/hotel/ar/cabanas-alpinas-terra-natura-bialet-masse.es.html).  
**Airbnb:** preparar listados alineados — `docs/AIRBNB_CHECKLIST.md` hasta tener login.

---

## Temporadas y precios

| Temporada | Período orientativo | Notas |
|-----------|---------------------|-------|
| **Alta verano** | Enero – Febrero | Pileta, demanda máxima |
| **Alta invierno** | Segunda quincena junio – Julio (vacaciones) | |
| **Media** | Fines de semana largos, octubre, marzo | |
| **Baja** | Resto del año, lun–jue | Workation, 4×3, retiros |

### Tarifas de referencia (ARS por noche) — dueño 2025/26

| Unidad | Verano (referencia dueño) | Notas PMS |
|--------|---------------------------|-----------|
| **Alpina 1, 2, 3** | **$110.000 – $120.000** | Publicar base 2 pax; suplemento menores opcional |
| **Suite 4, 5** | **$85.000 – $90.000** | Suite 4 PB sin A/A · Suite 5 PA con A/A (misma banda o +$5k Suite 5 en pico) |

### Precios temporada baja (referencia política dueño)

- **Tarifa noches viernes–domingo feriados (fin de semana en baja)** `B_finde`: se define como **porcentaje de la tarifa de verano** por tipo — completar número exacto cuando definas margen global (orientación típica 65–85 % según temporada). En PMS: `porcentaje_baja_sobre_verano_*` hasta que estén fijados pueden quedar `null`.

- **Noches lunes–jueves en temporada baja** `B_sem`: **−15 %** respecto del precio ya bajado de fin de semana en baja (`B_sem = B_finde × (1 − 0.15)`).

- **Promos en temporada baja** (combinables con política vigente cuando el motor lo permita):
  - **3×2:** pagás 2 noches, quedate 3 → equivalente **2/3** de la tarifa nominal por noche (−33,3 % promedio).
  - **4×3:** pagás 3 noches, quedate 4 → equivalente **3/4** de la tarifa nominal por noche (−25 % promedio).

Ejemplos numéricos y fórmulas detalladas: **`docs/TARIFAS_PROMOCIONES.md`**.

### Ejemplo rápido (solo ilustrativo, usá tus `B_finde`)

Si en baja el finde alpina vale `B_finde = $80.000` y `B_sem = $68.000` (−15 %):

| Paquete | Total a cobrar (noches todas a misma tarifa P) |
|---------|------------------------------------------------|
| 3 noches promo 3×2 con P=B_sem ($68k) | $136.000 (equiv. ~$45.333/noche) |
| 4 noches promo 4×3 con P=B_sem | $204.000 (equiv. ~$51.000/noche) |

**Tarifas verano siguen siendo ancla** (alpina `$110–120k`, suites `$85–90k`): la baja se deriva después con el % que cargues para `B_finde`.

---

**Booking vs directo**

\(\text{Precio listado Booking} \approx \text{Precio directo} × 1{,}18\) (± ajustes manuales en extranet si la comisión real difiere).

### Benchmark competencia (revisión periódica por AMA)

El agente debe **revisar mensualmente** (o antes de cada temporada alta) precios publicados en:
- [Alquiler Argentina — Bialet Massé](https://www.alquilerargentina.com/C%C3%B3rdoba/Caba%C3%B1as-en-Bialet-Mass%C3%A9/)
- [Paraírnos — cabañas Bialet Massé](https://www.parairnos.com/cabanas-en-bialet-masse)
- 3–5 complejos rivales en Google Maps (misma categoría: pileta, 2–4 pax)

**Última lectura mercado (orientativa):** promedio zona ~$77k/noche; rango $30k–$199k; loft complejos desde ~$100k; cabañas montaña 4–6 pax desde ~$160k.

**Conclusión vigente:** Alpina $110–120k = **competitiva** con buen valor (pileta, parque, balcón, cochera). Loft $85–90k = **atractiva** vs promedio y por debajo de muchos loft publicados. Ajustar ±5–10 % según ocupación real.

Informe en tablero: `mantener` | `subir $X` | `bajar $X` | `promo directa`.

---

## Promociones autorizadas (límites para IA / AMA)

| Promoción | Permitida | Tope descuento sin aprobación humana |
|-----------|-----------|--------------------------------------|
| Gap filler (1–2 noches libres) | Sí | **15 %** |
| **Lun–jue en baja vs finde baja** | Sí | **15 %** (sobre `B_finde`, ya en reglas) |
| **3×2 y 4×3 en baja** | Sí | Preaprobado (ver `TARIFAS_PROMOCIONES.md`) |
| Workation (≥7 noches) | Sí | **10 %** |
| Reseña Google → próxima estadía | Sí | **10 %** (definir en checkout) |
| Feriado puente last minute | Sí | **20 %** solo si ocupación < 40 % a 7 días |

---

## Guía local (base para QR y mensajes)

### Distancias de referencia
- Lago San Roque / Las Mojarras: **600 m**
- Centro Bialet Massé: **~2 km**
- Balneario Barrancas Bermejas (Cosquín): **~2 km**
- Autovía del Valle de Punilla (rotonda): **600 m**

### Dónde comer (lista dueño + exploración recomendaciones)

Orientativos · **confirmar siempre horario menú teleférico antes de salir**:

1. **Carrito Abilú** — rápido / ubicación cercana (**ver ubicación vigente en [Maps](https://www.google.com/maps/search/?api=1&query=Carrito+Abilu+Bialet)**).
2. **Rancho Stone** — pizza/pub; **Tel. +54 3541 441559** · Ruta 38 zona ([perfil público ejemplo](https://es.restaurantguru.com/). Revisión en tiempo real: buscar nombre en Maps).
3. **Veneto Village — restaurantes** — polo gastronómico cerca Carlos Paz (**en auto**) · opción especial cena ([búsqueda Maps](https://www.google.com/maps/search/?api=1&query=Veneto+Village+Carlos+Paz)).
4. **La Parrilla de Bialet** — parrilla / regional ([Maps](https://www.google.com/maps/search/?api=1&query=La+Parrilla+de+Bialet)).
5. **Alaska** — verificar ubicación actual en zona ([Maps](https://www.google.com/maps/search/?api=1&query=Alaska+restaurant+Bialet)).
6. **Explorador por calificaciones** — [Ranking Bialet — Restaurant Guru](https://es.restaurantguru.com/Bialet-Masse) *(opiniones de usuarios)*.

Otros cercanos conocidos por reseñas en la zona: **Proyecto Sierras** (Pueblo Viejo/Bialet) — chequear disponibilidad de horario · [ficha ejemplo](https://es.restaurantguru.com/).

### Para la Smart TV huésped

Guía navegable (**comer, almacenes, paseos, lluvia, gustos**) en carpeta **`guest-app/`**: abrir `index.html` en el navegador del TV con URL publicada (`?noches=5` opcional para filtrar sugerencias). Contenido editable en **`guest-app/data.json`**.

---

### Qué hacer
1. Lago San Roque y zona del dique
2. Arroyo Las Mojarras
3. Valle de Punilla (Cosquín, La Bolsa, río)
4. Balneario Barrancas Bermejas

### Emergencias
- **Emergencias:** 911 / 107 (same)
- **Salud más cercana:** [PENDIENTE — Bialet / Cosquín]

---

## Versión del documento

| Campo | Valor |
|-------|-------|
| Última actualización | 2026 |
| Confirmado por dueño | Inventario Alpina/Suite · seña · horarios · pileta 10–20 · WhatsApp/email · Booking público · baja lun–jue −15 % · promos 3×2 · 4×3 · efectivo −10 % · Booking +18 % · guía local comer · guest-app Smart TV |
| Pendiente opcional | % exacto **`B_finde` sobre verano** por alpina vs suite (`defaults.py` hasta `null`) · IG/FB URLs · salud/maps hospital preferido · mapeo color alpinas |
| Nombres unidades | Alpina 1·2·3 · Suite 4·5 |
