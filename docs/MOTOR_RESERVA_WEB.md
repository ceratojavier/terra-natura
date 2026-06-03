# Motor de reserva web ↔ PMS ↔ Booking

## Flujo central

1. **Booking** exporta iCal por unidad → el PMS importa cada **15 min** (job en Render) o manual `POST /api/canales/sync-ical`.
2. Reserva nueva → estado `confirmada`, `origen=booking`, alerta en panel + WhatsApp al dueño (si Cloud API configurada).
3. Cancelación en Booking → desaparece del iCal → PMS marca `cancelada`.
4. **Export** PMS → Booking importa ocupación (web + manual + Booking) → anti overbooking.
5. **Web** cotiza con `POST /api/cotizar` → `disponibilidad_service` ve las mismas noches ocupadas.

## Endpoints

| Método | Ruta | Uso |
|--------|------|-----|
| GET | `/api/public/motor-reserva` | Config para el JS (unidades, reglas, URLs) |
| POST | `/api/cotizar` | Precio + flag `disponible` |
| POST | `/api/reservas/operacion` | Alta manual confirmada (panel móvil) |
| POST | `/api/reservas` | Pre-reserva web (`origen=web_directa`) |
| POST | `/api/canales/sync-ical` | Import manual Booking |
| GET | `/api/canales/alertas` | Avisos reservas Booking / solapes |
| POST | `/api/canales/alertas/leer` | Marcar alertas leídas |
| GET | `/api/canales/estado` | Feeds iCal + último sync |
| POST | `/api/webhooks/whatsapp` | Consultas clientes (cotiza + responde) |
| GET | `/api/unidades/{id}/ical` | Export ocupación hacia Booking |

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
