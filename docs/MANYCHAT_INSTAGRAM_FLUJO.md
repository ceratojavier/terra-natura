# ManyChat — Instagram Terra Natura (INFO / PRECIO)

Textos listos para copiar. Tono: cálido, hospitalario, profesional.  
WhatsApp: `[NUMERO_WHATSAPP]` (ej. 5493541571190). Web: `https://alpinasterranatura.com.ar`

---

## 1. Disparador (comentario → DM automático)

**Palabras clave:** `INFO`, `PRECIO`, `RESERVA`, `DISPONIBLE`

**Primer mensaje DM:**

> Hola, [nombre] 👋  
> Gracias por escribir desde Instagram. Soy el asistente de **Cabañas Alpinas Terra Natura** (Bialet Massé, sierras de Córdoba).  
> En un paso te ayudo con fechas y tipo de viaje — así te pasamos al equipo de reservas con todo listo.  
> **¿Qué tipo de escapada buscás?**

**Botones:**

- `Escapada en pareja` → flujo pareja  
- `Viaje en familia` → flujo familia  
- `Consulta general` → flujo general  

---

## 2. Calificación (máximo 2 pasos)

### Paso 1 — Tipo (ya elegido arriba)

**Si pareja:**

> Perfecto 💚 Para parejas recomendamos **Alpina** (espacio y balcón) o **Suite** (loft íntimo).  
> **¿Cuántas noches tenés pensadas?**

Botones: `2 noches` · `3 noches` · `4 o más` · `Aún no sé`

### Paso 2 — Fechas aproximadas

> Genial. **¿En qué mes o fechas querés venir?** (ej. «finde 22 junio» o «julio vacaciones»)

Botones: `Este mes` · `Próximo mes` · `Escribo fechas` (abre campo texto)

*(ManyChat: guardar custom fields `tipo_viaje`, `noches`, `fechas_texto`)*

---

## 3. Cierre + WhatsApp

> Listo, [nombre]. Resumen: **[tipo_viaje]** · **[noches]** · **[fechas_texto]**  
>  
> Terra Natura: 5 cabañas, pileta y parque, a **600 m del lago San Roque**. Reserva directa sin comisión de plataforma.  
>  
> Tocá el botón y hablá con reservas por WhatsApp (mensaje ya armado):

**Botón URL WhatsApp:**

```
https://wa.me/[NUMERO_WHATSAPP]?text=Hola%2C%20vi%20el%20Instagram%20de%20Terra%20Natura.%20Quiero%20cotizar%20para%20[TIPO_VIAJE]%20-%20[NOCHEs]%20noches%20-%20fechas%3A%20[FECHAS].%20%C2%BFHay%20disponibilidad%3F
```

**Texto visible del botón:** `Cotizar por WhatsApp`

**Mensaje prellenado (legible):**

> Hola, vi el Instagram de Terra Natura. Quiero cotizar para [pareja/familia] — [X] noches — fechas: […]. ¿Hay disponibilidad?

---

## Variante PRECIO (comentario en Reel promocional)

Disparador igual; primer DM añade:

> Si venís en **temporada baja** preguntanos por **4 noches y te quedás 5**. En **julio**, **5 noches + la 6.ª bonificada** (según disponibilidad).

*(No inventar cifras en el bot si no están actualizadas — derivar siempre a humano/WhatsApp para monto final.)*

---

## Integración con el ecosistema Terra Natura

| Herramienta | Rol |
|-------------|-----|
| **ManyChat** | Captura IG → califica → WhatsApp |
| **WhatsApp Business + IA Meta** | Respuestas 24/7, FAQ, handoff humano — ver `WHATSAPP_BUSINESS_IA_MAXIMO.md` |
| **PMS / pricing_engine** | Cotización real cuando el humano o la API interna consulte fechas |
| **AMA** | Copy de posts y respuestas alineadas a `docs/COPY_TONO_MARCA.md` |

---

## Checklist de configuración ManyChat

1. Conectar cuenta Instagram Business a ManyChat.  
2. Automation → **Instagram Comments** → keyword `INFO`, `PRECIO`.  
3. Acción: **Send DM** con mensaje disparador + botones.  
4. Custom fields + condición por botón (2 pasos máx.).  
5. Último paso: **Open Website** o **WhatsApp** con URL `wa.me`.  
6. Probar desde cuenta personal comentando en un post de prueba.
