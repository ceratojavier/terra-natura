# Mercado Pago — Webhook e integración (Terra Natura)

## URLs en producción

Reemplazá `TU_DOMINIO` por `https://alpinasterranatura.com.ar` (o tu URL de Vercel).

| Uso | URL |
|-----|-----|
| Webhook (notificaciones IPN) | `TU_DOMINIO/api/webhooks/mercadopago` |
| Retorno éxito | `TU_DOMINIO/reserva/exito` |
| Retorno fallo | `TU_DOMINIO/reserva/fallo` |
| Retorno pendiente | `TU_DOMINIO/reserva/pendiente` |

## Configurar en Mercado Pago

1. Entrá a [Tus integraciones](https://www.mercadopago.com.ar/developers/panel/app).
2. Elegí la aplicación de **producción** (o pruebas para sandbox).
3. **Webhooks** → **Configurar notificaciones**.
4. Modo: **Producción** (o pruebas).
5. URL: `https://alpinasterranatura.com.ar/api/webhooks/mercadopago`
6. Eventos: marcá **Pagos** (`payment`).
7. Guardá.

## Variables en Vercel / `.env.local`

```env
MERCADOPAGO_ACCESS_TOKEN=APP_USR-...   # producción
NEXT_PUBLIC_SITE_URL=https://alpinasterranatura.com.ar
```

En **pruebas** usá credenciales de prueba y `NEXT_PUBLIC_SITE_URL` con la URL de preview de Vercel.

## Flujo del sistema

1. El huésped paga la **seña 50%** en `/reservar`.
2. MP redirige a éxito/fallo/pendiente.
3. MP envía POST al webhook con `type: payment` y `data.id`.
4. La app consulta `GET /v1/payments/{id}` y, si `status === approved`:
   - Marca la reserva como `confirmada` / `senado`
   - Bloquea fechas en calendario
   - Envía email (si `RESEND_API_KEY` está configurada)

## Probar el webhook en local

Usá [ngrok](https://ngrok.com/) o similar:

```bash
ngrok http 3000
```

En MP, URL de prueba: `https://xxxx.ngrok.io/api/webhooks/mercadopago`

Y en `.env.local`:

```env
NEXT_PUBLIC_SITE_URL=https://xxxx.ngrok.io
```

## Cron iCal (Booking)

En Vercel, `vercel.json` ya programa sync cada 6 h. Manual:

```http
GET /api/cron/sync-ical
Authorization: Bearer {CRON_SECRET}
```

## Checklist antes de salir a producción

- [ ] `MERCADOPAGO_ACCESS_TOKEN` de producción en Vercel
- [ ] Webhook MP apuntando al dominio final
- [ ] `NEXT_PUBLIC_SITE_URL` = dominio final
- [ ] Supabase con schema + seed ejecutados
- [ ] `ICAL_*` en variables de entorno
- [ ] Probar un pago real de monto bajo
