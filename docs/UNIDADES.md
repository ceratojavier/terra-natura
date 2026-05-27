# Fichas de unidades — Terra Natura

## Complejo

- **Nombre:** Cabañas Alpinas Terra Natura  
- **Dirección:** Los Talas 759, Bialet Massé, Córdoba  
- **Superficie predio:** ~2.000 m²  
- **Unidades alquilables:** 5 (3 alpinas + 2 lofts)  
- **Casa de los dueños:** **Dentro del complejo**, en el mismo predio de 2.000 m² — conviven anfitriones y huéspedes; **no se alquila** ni se sincroniza con Booking/Airbnb

---

## Alpinas 1, 2 y 3 — 2 plantas

**Nombres comerciales:** **Alpina 1** · **Alpina 2** · **Alpina 3**  
**Código interno:** `alpina-1`, `alpina-2`, `alpina-3`

### Distribución

| Planta | Ambientes y equipamiento |
|--------|--------------------------|
| **Planta baja** | **6 m × 5,5 m** (~33 m²) — living-comedor integrado (incluye **baño** y **cocina con barra desayunadora**) · **2 camas de 1 plaza** · **Heladera con freezer** · horno |
| **Planta alta** | **Dormitorio matrimonial** · **Aire acondicionado frío/calor** · **Balcón con vista panorámica al Valle de Punilla** |

### Baño y confort
- Baño completo con **ducha**
- **Smart TV** (TV por internet — Netflix, YouTube)
- **WiFi**
- **Ropa blanca:** sábanas, toallas, ropa de cama de **abrigo**

### Exterior privado (por cabaña)
- **Pérgola** con bancos, mesa y **asador**
- Acceso a **estacionamiento techado** (media sombra del complejo)

### Capacidad y venta
| Campo | Valor |
|-------|-------|
| Capacidad máxima técnica | 4 personas |
| Recomendado marketing | **2 adultos** — “súper cómoda para parejas” |
| Uso camas PB | **Niños** — no 4 adultos |
| Living PB | **33 m²** — argumento central de amplitud en fotos y copy |
| OTA / web — título sugerido | *Cabaña alpina · living 33 m² · balcón al Valle de Punilla — ideal parejas* |

### Fotos prioritarias (Drive)
- Balcón vista valle (atardecer)
- Dormitorio matrimonial PA
- Living PB despejado
- Pérgola y asador
- Fachada / entrada

---

## Suite 4 y Suite 5 — lofts en dúplex

Dos unidades monoambiente con **entrada independiente** (planta baja y planta alta del mismo dúplex).

### Suite 4 — planta baja (`suite-4`) ✅ confirmado PB del dúplex

| Atributo | Detalle |
|----------|---------|
| **Ambiente** | Monoambiente único · entrada independiente |
| **Camas** | 1 matrimonial + 1 de 1 plaza |
| **Climatización** | **Ventilador de techo** (sin aire acondicionado) |
| **Resto de servicios** | Igual que alpinas: cocina, heladera freezer, horno, baño ducha, Smart TV, WiFi, ropa blanca, pérgola con asador |

**Público ideal (hoy):** Pareja; pareja + 1 niño; quien prefiera planta baja sin escaleras.

**En evaluación:** uso alternativo como **salón / desayuno** (dejar de alquilar) — ver `docs/DECISION_SUITE4.md`. Arriba: Suite 5.

### Suite 5 — planta alta (`suite-5`) ✅ confirmado PA del dúplex

| Atributo | Detalle |
|----------|---------|
| **Ambiente** | Monoambiente único · entrada independiente |
| **Camas** | 1 matrimonial + 1 de 1 plaza |
| **Climatización** | **Aire acondicionado frío/calor** |
| **Resto de servicios** | Idem Suite 4 |

**Público ideal:** Pareja que prioriza A/A; único loft de alquiler si Suite 4 pasa a salón común.

### Capacidad suites 4 y 5
| Campo | Valor |
|-------|-------|
| Capacidad máxima | 3 personas |
| Recomendado marketing | **2 adultos** (+ 1 niño en cama 1 plaza) |

### Fotos prioritarias (Drive)
- Suite 4: interior, pérgola, ventilador
- Suite 5: interior, A/A, vista si aplica
- Entradas independientes (mostrar que son unidades separadas)

---

## Áreas comunes (todas las unidades)

| Área | Especificación |
|------|----------------|
| Pileta | 6 m × 3 m, prof. 1,50 m, descubierta |
| Solarium | Reposeras |
| Parque | Hamacas, casita niños, ~2.000 m² |
| Estacionamiento | Techado, media sombra |

---

## Matriz rápida para el PMS (seed)

```json
[
  {"id": "alpina-1", "tipo": "alpina", "nombre": "Alpina 1", "numero": 1, "pb_m2": 33, "precio_verano": [110000, 120000], "cap_max": 4, "cap_recomendada": 2},
  {"id": "alpina-2", "tipo": "alpina", "nombre": "Alpina 2", "numero": 2, "pb_m2": 33, "precio_verano": [110000, 120000], "cap_max": 4, "cap_recomendada": 2},
  {"id": "alpina-3", "tipo": "alpina", "nombre": "Alpina 3", "numero": 3, "pb_m2": 33, "precio_verano": [110000, 120000], "cap_max": 4, "cap_recomendada": 2},
  {"id": "suite-4", "tipo": "suite", "nombre": "Suite 4", "numero": 4, "planta": "baja", "precio_verano": [85000, 90000], "cap_max": 3, "cap_recomendada": 2},
  {"id": "suite-5", "tipo": "suite", "nombre": "Suite 5", "numero": 5, "planta": "alta", "precio_verano": [85000, 90000], "cap_max": 3, "cap_recomendada": 2}
]
```
