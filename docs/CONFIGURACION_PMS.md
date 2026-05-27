# Guía de configuración — Terra Natura PMS

Todo lo que podés cambiar **sin programar**: desayuno, 5 cabañas on/off, transformar una unidad en salón, OTAs, seña.

**Estado inicial (hoy):**
- 5 unidades **alquilables** (Alpina 1–3, Suite 4–5)
- Desayuno **deshabilitado**
- Suite 4 y 5 en modo **independiente**

---

## Arrancar el servidor

```bash
cd "Proyecto Terra Natura"
pip install -r backend/requirements.txt
python -m backend.app
```

API: http://localhost:8000/docs

---

## 1. Ver estado del complejo

`GET /api/config/resumen`

Muestra cuántas unidades están reservables, si el desayuno está activo, canales, etc.

---

## 2. Desayuno (hoy: NO)

**Ver:** `GET /api/config/desayuno`

**Activar cuando quieras:**

```http
PATCH /api/config/desayuno
Content-Type: application/json

{
  "habilitado": true,
  "incluido_en_tarifa": false,
  "precio_por_persona_ars": 5000,
  "horario_inicio": "08:00",
  "horario_fin": "10:30",
  "unidad_salon_id": "suite-4"
}
```

**Desactivar de nuevo:**

```json
{ "habilitado": false }
```

Si usás Suite 4 como salón, además:

```http
PATCH /api/unidades/suite-4
{
  "uso_modo": "salon_desayuno",
  "alquilable": false,
  "visible_ota": false
}
```

---

## 3. Una cabaña: desactivar o cambiar de uso

`PATCH /api/unidades/{id}`

| Campo | Ejemplo | Efecto |
|-------|---------|--------|
| `activa` | `false` | Apagada en todo el sistema |
| `alquilable` | `false` | No entra en calendario |
| `uso_modo` | `salon_desayuno` | Deja de ser alquiler |
| `visible_ota` | `false` | No sincronizar Booking/Airbnb |
| `visible_web` | `false` | Oculta en web propia |

**Ejemplo — Suite 4 solo salón (futuro):**

```json
{
  "uso_modo": "salon_desayuno",
  "alquilable": false,
  "visible_ota": false,
  "activa": true
}
```

**Ejemplo — Alpina 2 en mantenimiento:**

```json
{
  "uso_modo": "mantenimiento",
  "alquilable": false,
  "activa": true
}
```

**Volver a alquilar:**

```json
{
  "uso_modo": "alquiler",
  "alquilable": true,
  "visible_ota": true,
  "visible_web": true
}
```

`uso_modo` posibles: `alquiler` · `salon_desayuno` · `salon_comedor` · `espacio_comun` · `mantenimiento` · `fuera_servicio` · `uso_familiar`

---

## 4. Regla rápida Suite 4 / 5

`PATCH /api/config/suite4-reglas`

| modo | Qué hace |
|------|----------|
| `independiente` | Las 5 se alquilan (default hoy) |
| `hibrido` | Guardado para fase reservas (bloqueo automático) |
| `solo_salon` | Suite 4 → salón, no alquilable |

---

## 5. Solo reserva directa (sin Booking/Airbnb)

```http
PATCH /api/config/canales
{ "modo_solo_reserva_directa": true }
```

Vuelve a abrir OTAs: `false` y `booking_habilitado` / `airbnb_habilitado` en `true`.

---

## 6. Seña, horarios, mascotas

`PATCH /api/config/reservas` vía PUT:

```http
PUT /api/config/reservas
{
  "valor": {
    "porcentaje_sena": 50,
    "plazo_sena_horas": 48,
    "check_in": "11:30",
    "check_out": "10:00",
    "deposito_garantia": false,
    "mascotas_pequenas": true,
    "mascotas_no_solas_en_unidad": true
  },
  "merge": true
}
```

---

## Panel web (próxima fase)

La misma lógica irá en `frontend/pages/configuracion.html` con interruptores visuales.
