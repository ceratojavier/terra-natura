# Motor de reserva web ↔ PMS ↔ Booking

## Flujo

1. **Booking** exporta iCal por unidad → `POST /api/canales/sync-ical` importa bloqueos como reservas `confirmada` con `origen=booking`.
2. **Web** cotiza con `POST /api/cotizar` → `disponibilidad_service` ve las mismas noches ocupadas.
3. **Booking/Airbnb** importan ocupación del PMS → `GET /api/unidades/{id}/ical?token=…`.

## Endpoints

| Método | Ruta | Uso |
|--------|------|-----|
| GET | `/api/public/motor-reserva` | Config para el JS (unidades, reglas, URLs) |
| POST | `/api/cotizar` | Precio + flag `disponible` |
| POST | `/api/reservas/operacion` | Alta manual confirmada (panel móvil) |
| POST | `/api/reservas` | Pre-reserva web (`origen=web_directa`) |
| POST | `/api/canales/sync-ical` | Sincronizar feeds Booking (cron o agente Channel) |
| GET | `/api/canales/estado` | Diagnóstico feeds |

## GitHub Pages + API en VM

En `frontend/public/assets/data/site-config.json`:

```json
{
  "apiBase": "https://tu-servidor-pms.example.com"
}
```

Sin `apiBase`, la home en Pages usa tarifa **estimada local** (fallback).

## Cron sugerido

Cada 15–30 min: `curl -X POST https://…/api/canales/sync-ical`
