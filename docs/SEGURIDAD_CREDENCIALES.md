# Seguridad — credenciales Terra Natura

## Regla de oro

- **Nunca** subir contraseñas al repositorio Git, ni a `AGENTS.md`, ni a `docs/` con texto plano.
- **Nunca** pegar contraseñas en chats con IA (quedan registradas). Si ya lo hiciste: **cambiá todas esas claves ahora** (Booking extranet, Gmail, Google Business).

## Dónde guardar secretos (solo en tu máquina)

Creá un archivo `.env` en la raíz del proyecto (está en `.gitignore`) con variables como:

```
BOOKING_PARTNER_USER=
BOOKING_PARTNER_PASSWORD=
GMAIL_APP_PASSWORD=
OPENAI_API_KEY=
```

Usá `.env.example` sin valores reales como plantilla.

## Gestión de Booking / Gmail / Meta

- Activá **verificación en dos pasos** donde exista.
- Para integraciones, preferí **contraseñas de aplicación** (Gmail) o **tokens OAuth** en lugar de la clave principal del correo.

## Enlaces de Booking

Usá la URL pública del hotel **sin** parámetros `label=`, `sid=`, etc. (solo la ruta del establecimiento).

## Contacto público sí puede ir en docs

WhatsApp público de reservas, email `terranaturaalpinas@gmail.com`, enlaces públicos Booking / Google Maps: **OK** en documentación.
