# Qué pedís vos · qué hay hoy · qué falta (Terra Natura)

Documento para el dueño: sin código, sin vueltas.

## Lo que más te importa (tu lista)

| Querés | Estado hoy | Por qué todavía no está “vivo” |
|--------|------------|----------------------------------|
| **Un agente (IA) que automatice publicaciones, anuncios y redes** | Idea y reglas en `AGENTS.md` · carpeta `ama/` empieza en el repo | Hace falta **cuentas Meta (Facebook/Instagram)**, **tokens**, y en muchos casos **aprobar la app** con Meta. Sin eso no se puede “subir solo” a Instagram. |
| **WhatsApp automático** según el tipo de consulta | No conectado | WhatsApp Business **API Cloud** (Meta) o **proveedores** (Twilio, etc.) = **costo / registro / número verificado**. El sitio hoy puede cotizar y listar reservas; **no** recibe mensajes de WhatsApp dentro del programa hasta enganchar esa API. |
| **Actualización del channel manager** (Booking, Airbnb, todo unificado) | **Export** iCal por unidad (bloqueos) · **Import** desde OTAs todavía no | Channel manager **real** (API Booking/Airbnb) es de **pago** o contrato OTA. El plan acordado en el documento del proyecto era **MVP con iCal** (gratis) y API después si el volumen lo pide. |
| **Registro de reservas** | **Sí hay** modelo, API y panel simple para ver y crear vía API | Falta: **cobro MP**, **seña 48 h**, **jobs** que cancelen solas, **mensajes automáticos** (RQ-17). |

## Qué sí tenés ya (base necesaria)

Sin esto no podría existir después el “cerebro” que cotiza y responde con datos reales:

- Unidades, configuración, **cotización** con temporadas y promos.
- **Disponibilidad** y **reservas** en base.
- **Panel** web para vos (lectura de reservas, enlaces, cotizar).
- **iCal de salida** por unidad (para pegar en Airbnb/Booking y que vean ocupación).

Eso es **PMS + datos**; **no** es todavía el AMA completo ni WhatsApp entrante.

## Orden lógico de lo que viene (alineado a `AGENTS.md`)

1. **WhatsApp saliente** desde el sistema (avisos, plantillas) cuando haya API y plantillas aprobadas.  
2. **Webhook WhatsApp entrante** → reglas simples → si consulta de disponibilidad, usar **mismo motor** que la web (`/api/cotizar`, `/api/reservas`).  
3. **AMA**: calendario de posts, borradores, modo aprobación; después **Meta** para publicar.  
4. **Import iCal** desde Airbnb/Booking hacia el PMS (bloqueos externos).  
5. Channel manager por **API** solo si el negocio justifica el costo.

## Cómo se te “ve” el trabajo del agente adentro

Cuando avancemos, el panel va a tener una zona **“Marketing y mensajes”** (estado real: conectado / pendiente token / modo borrador). Hoy el código empieza a existir bajo `ama/` y webhooks de prueba; **no reemplaza** todavía a una persona en redes hasta conectar APIs.

Si querés priorizar **una sola cosa** para el próximo sprint de desarrollo, conviene definir: **WhatsApp Cloud API** (Meta) **o** **borradores de posts + calendario AMA sin publicar** (sin riesgo de cuenta).
