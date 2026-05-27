# 🏔️ TERRA NATURA — ECOSISTEMA DIGITAL INTEGRAL (Bialet Massé, Córdoba)

**Nombre comercial:** Cabañas Alpinas Terra Natura  
**Dirección:** Los Talas 759, Bialet Massé, Córdoba, Argentina  
**Predio:** ~2.000 m² (parque con pileta, área común, casa de dueños en el mismo lote)  
**Unidades de alquiler:** **5** (3 alpinas + 2 lofts)

| Tipo | Cantidad | Layout | Posicionamiento |
|------|----------|--------|-----------------|
| **Cabañas Alpinas** | **3** | PB: living-comedor + 2×1 plaza + cocina/horno/freezer · PA: matrimonial + A/A + **balcón vista Valle de Punilla** | **Híbrido:** parejas / familia con niños (ver §1.1) |
| **Suites 4 y 5** | **2** | Lofts en dúplex, **entradas independientes** (Suite 4 PB · Suite 5 PA): matrimonial + 1 plaza | Parejas (+1 niño); Suite 4 ventilador · Suite 5 A/A |

**Ubicación clave:** 600 m Lago San Roque, Arroyo Las Mojarras, rotonda Autovía Punilla · ~2 km centro Bialet y balneario Barrancas Bermejas.

**Reglas de negocio detalladas:** `docs/REGLAS_NEGOCIO.md` · **Fichas unidades:** `docs/UNIDADES.md`

**Valor diferencial:** Los dueños **viven en su casa dentro del complejo** (mismo predio de 2.000 m²) — recepción cercana, asistencia rápida; la vivienda familiar **no** es unidad de alquiler ni entra al PMS (ver `docs/REGLAS_NEGOCIO.md` § Casa de los dueños).

**Visión del proyecto:** Dos sistemas que comparten datos pero cumplen misiones distintas:
1. **PMS Terra Natura** — Software de gestión + channel manager + web con reservas.
2. **Agente de Marketing Autónomo (AMA)** — Contenido, redes, eventos, ofertas, comunicación pre/durante/post estadía.

> **Para Cursor / agentes de IA:** Leer este archivo completo antes de codificar. Respetar IDs `RQ-XX`, fases y prioridad **gratis primero**. Actualizar checklists al cerrar cada requerimiento.

---

## 1. DECISIONES DE NEGOCIO (YA DEFINIDAS)

### 1.1 Capacidad Cabañas Alpinas — Modelo Híbrido Optimizado ✅

**Problema de “4 justos”:** Dos camas en living/cocina aprietan a 4 adultos y restan privacidad.  
**Oportunidad parejas:** Mayor ticket promedio, mejor cuidado del inmueble, fotos más aspiracionales.

**Decisión de producto:**
- **Vender como:** *“Refugio romántico y amplio para 2 · apto familias con niños”*.
- **Camas PB:** Presentar como *diván / camas auxiliares* para **niños**, no como dormitorio principal para 4 adultos.
- **En sistema y OTAs:** Capacidad máxima técnica `4` (2 adultos + 2 menores) con flag `recomendado_parejas: true`.
- **En copy y fotos:** Protagonizar dormitorio matrimonial PA + living despejado.

**Mejoras sin costo (dueño / operaciones):**
- Mejor luz cálida en dormitorio PA.
- Living despejado para sensación de amplitud en fotos y estadía.
- Cartelería: “Diseñado para parejas · capacidad flexible con menores”.

### 1.2 Suites 4 y 5 (lofts monoambiente)
- **Capacidad máx. 3** (matrimonial + 1 plaza); **vender como pareja** (+ niño en cama simple).
- **PB:** ventilador de techo, sin A/A — ideal quien evita escaleras.
- **PA:** A/A frío-calor — ideal verano Punilla.
- Mismos servicios que alpinas (cocina, Smart TV, WiFi, pérgola, asador, ropa blanca).

### 1.3 Usos alternativos del predio (2.000 m²) — Ideas para AMA y temporada baja
- **Retiros bienestar** (yoga/meditación) — alquiler bloque semana en baja.
- **Workation** — estadías 7–15 noches lun–vie, WiFi + silencio.
- **Eventos privados** — cumpleaños, aniversarios en parque (sin ruido excesivo; reglas en `docs/REGLAS_NEGOCIO.md`).
- **Bloqueo corporativo** — empresas locales (capacitaciones en Punilla).

---

## 2. IDENTIDAD DEL AGENTE DE MARKETING (AMA) — “CEREBRO” CONVERSACIONAL

### 2.1 Rol
**Gerente de Operaciones Digitales y Marketing Turístico — Terra Natura**

### 2.2 Personalidad y tono
- Anfitrión cálido, conocedor de **Valle de Punilla / Bialet Massé / Dique San Roque**.
- Español rioplatense **cordobés sutil** (vos/te, sin exagerar lunfardo).
- Cercano, profesional, nunca robot frío.
- En consultas: técnica de cierre suave (*disponibilidad → beneficio → CTA WhatsApp/link pago*).

### 2.3 Objetivos AMA (Task Master)
| Área | Entregable |
|------|------------|
| Contenido | Calendario mensual IG, FB, Google Business, WhatsApp Status |
| Ventas | Ofertas temporada baja, gap filler, feriados puente |
| Atención | Respuesta consultas + derivación a reserva/pago |
| Experiencia | Guía local dinámica (QR), pre-arribo, post-salida reseñas |
| Inteligencia | Scraping eventos Córdoba → post segmentado por audiencia |

### 2.4 Modos de operación (Tablero de Control)
| Modo | Comportamiento |
|------|----------------|
| 🟢 **Automático** | Publica según calendario + eventos sin aprobación |
| 🟡 **Aprobación** | Genera borrador → dueño confirma en dashboard → publica |
| ⚡ **Acción inmediata** | Prompt en tablero: *“Post de último momento, salió el sol…”* → escanea Drive → borrador → confirmar → publicar |

---

## 3. CICLO DE VIDA DEL PROYECTO (REQUISITOS → DISEÑO → CÓDIGO → OPERACIÓN)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  DISCOVERY  │───▶│   DISEÑO    │───▶│    BUILD    │───▶│   RUN OPS   │
│  Fase 0     │    │  Fase 0-1   │    │  Fase 1-8   │    │  AMA + PMS  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### FASE 0 — Discovery y diseño (Semana 1–2)
- [x] Completar `docs/REGLAS_NEGOCIO.md` (inventario 5 u., seña 50 %, horarios, ubicación, amenities).
- [ ] Pendiente en reglas: WhatsApp, precios ARS, mascotas, depósito garantía, URLs OTA.
- [ ] Inventario fotográfico en Google Drive (estructura §12).
- [ ] Mapa de canales actuales (Airbnb, Booking, directo, WhatsApp).
- [ ] Diagrama arquitectura: `docs/ARQUITECTURA.md`.
- [ ] Wireframes: web pública, panel staff, tablero AMA.
- [ ] Definir MVP vs. V2 (channel manager API vs. solo iCal).

### FASE 1 — Fundamentos PMS (Semana 3–4)
- [ ] RQ-01 a RQ-03 (unidades, tarifas, usuarios).

### FASE 2 — Reservas y anti-overbooking (Semana 5–7)
- [ ] RQ-04 a RQ-06 + sincronización iCal básica.

### FASE 3 — Huéspedes y comunicación (Semana 8–9)
- [ ] RQ-07 a RQ-09 + plantillas pre/durante/post.

### FASE 4 — Finanzas (Semana 10–11)
- [ ] RQ-10 a RQ-12 + Mercado Pago (sandbox → prod).

### FASE 5 — Operaciones (Semana 12–13)
- [ ] RQ-13 a RQ-16 (limpieza, mantenimiento, tablero operativo).

### FASE 6 — AMA Core (Semana 14–16)
- [ ] RQ-M01 a RQ-M06 (eventos, contenido, publicador, calendario estacional).

### FASE 7 — Web y conversión (Semana 17–18)
- [ ] RQ-20, RQ-M07, landing dinámica, SEO local.

### FASE 8 — Channel manager y revenue (Semana 19–20)
- [ ] RQ-21, RQ-M08, RQ-M09 (iCal/API, precios dinámicos, gap filler).

### FASE 9 — Tablero unificado + deploy (Semana 21–22)
- [ ] RQ-M10 Dashboard Streamlit o panel web integrado.
- [ ] Deploy VM + documentación operativa.

---

## 4. MÓDULO PMS — REQUERIMIENTOS FUNCIONALES

### MÓDULO 1: Catálogo

#### RQ-01: Unidades (**5** registros fijos — ver `docs/UNIDADES.md`)
- Tipos: `alpina` | `loft`
- IDs: `alpina-1`, `alpina-2`, `alpina-3`, `suite-4`, `suite-5`
- Nombres: **Alpina 1·2·3** · **Suite 4·5**
- Alpina: `capacidad_max=4`, `capacidad_recomendada=2`, balcón vista, A/A en dormitorio PA
- Suite: `capacidad_max=3`, `capacidad_recomendada=2`; `tiene_aire_acondicionado` solo en `suite-5`
- Amenities comunes: WiFi, Smart TV, ropa blanca abrigo, pérgola+asador, estacionamiento techado
- Complejo: pileta 6×3×1,5 m, solarium, hamacas, casita niños

#### RQ-02: Temporadas, feriados Argentina, precios
- Alta: Verano (ene–feb + julio vacaciones invierno)
- Media / Baja
- Feriados puente: tabla con alerta **60 días antes** (dispara AMA)
- Motor: `backend/services/pricing_engine.py`

#### RQ-03: Usuarios staff (dueños en predio = rol admin)

### MÓDULO 2: Reservas

#### RQ-04: Disponibilidad — **crítico**
- Transaccional, bloqueo por noche, estados unidad.

#### RQ-05: Reservas multicanal
- Origen: `web_directa` | `whatsapp` | `booking` | `airbnb` | `otro`
- Vincular ID externo de OTA.

#### RQ-06: Estados y seña
- **Seña 50 %** · plazo **48 h** · saldo 50 % pre check-in (ver `docs/REGLAS_NEGOCIO.md` cancelación).
- `pre_reserva` → `pendiente_pago` → `confirmada` → … → `cerrada`
- Job: liberar si no hay seña en 48 h; aplicar tabla cancelación (15 / 8–15 / ≤7 días).

### MÓDULO 3: Huéspedes

#### RQ-07: Ficha huésped  
#### RQ-08: Check-in digital  
#### RQ-09: Reglamento + consentimiento (versión PDF/QR)

### MÓDULO 4: Finanzas

#### RQ-10: Cobros (seña, saldo, extras)  
#### RQ-11: Comprobantes / Mercado Pago webhook  
#### RQ-12: Caja y reportes

### MÓDULO 5: Operaciones

#### RQ-13: Orden limpieza post-checkout  
#### RQ-14: Mantenimiento  
#### RQ-15: Inventario insumos (opcional MVP)  
#### RQ-16: Tablero operativo unidades (colores por estado)

### MÓDULO 6: Comunicación automatizada (PMS + AMA)

#### RQ-17: Plantillas mensajes
| Momento | Canal | Contenido |
|---------|-------|-----------|
| Consulta | WhatsApp / web | Disponibilidad, precio, CTA |
| Confirmación pago | WhatsApp + email | Voucher, política cancelación |
| T−24 h | WhatsApp | Ubicación, WiFi, guía QR, comer en Bialet |
| Check-in día | WhatsApp | Bienvenida, reglas fogón/ruido |
| Durante | QR en cabaña | Guía local dinámica |
| T+48 h post checkout | WhatsApp | Agradecimiento + link reseña Google |

#### RQ-18: Jobs APScheduler / cron  
#### RQ-19: Webhook Mercado Pago → confirmación + pack bienvenida

### MÓDULO 7: Web y analytics

#### RQ-20: Sitio web con reservas online
- SEO: *Cabañas Bialet Massé*, *alojamiento cerca Dique San Roque*
- Landing por campaña (UTM) generada desde AMA
- Social proof: reseñas Google (manual MVP → API V2)

#### RQ-21: Channel Manager — centralización
**Motor único de calendario** + reserva directa (web/WhatsApp).

**Canales:** Booking + Airbnb + directa — configuración de fichas/fotos desde panel (AMA genera briefs; dueño o dev carga en OTA).

**Interruptor `modo_solo_reserva_directa`** en `config_canales`:
- `true` → OTAs pausadas, solo web/WhatsApp; AMA no promociona OTA.
- `false` → sync iCal bidireccional Airbnb + Booking.

**MVP sin costo:** iCal bidireccional. **V2:** API Channex/Beds24 si el volumen lo exige.

#### RQ-22: Export contable CSV/PDF

---

## 5. MÓDULO AMA — MARKETING AUTÓNOMO

### RQ-M01: El Sabueso (Event Scraper)
**Fuentes diarias (scraping ético / RSS / APIs públicas):**
- Turismo Córdoba, agenda cultural Punilla
- Recitales Plaza Próspero Molina (Cosquín), Kempes, Villa María
- Rally, maratones, trail running, ferias artesanales Bialet Massé
- Feriados nacionales + puente (calendario Argentina)

**Salida estructurada:**
```json
{
  "evento": "Cosquín Rock",
  "fecha_inicio": "2026-02-15",
  "ubicacion": "Cosquín",
  "tags": ["musica", "jovenes", "parejas"],
  "audiencia": ["parejas", "grupos_amigos"],
  "unidad_sugerida": ["alpina", "suite"]
}
```

**Archivos:** `ama/scrapers/event_hunter.py`, `ama/data/eventos_cache.json`

### RQ-M02: El Estratega (Content Engine)
**Lógica si/evento:**
| Evento | Unidad | Copy angle |
|--------|--------|------------|
| Recital / festival | Alpinas + Lofts | “Tu refugio después del show — 600 m del lago” |
| Trail / rally / maratón | Alpinas | “Descansá cerca del circuito” |
| Relax / feriado puente | Lofts + Alpinas (parejas) | “Escapada express 3 noches en Punilla” |
| Familia (vacaciones julio) | Alpinas con niños | “Espacio para chicos, tranquilidad para vos” |

- Redacción ES-AR, emojis moderados, CTA WhatsApp con mensaje prellenado.
- Selección imagen desde Drive por tags (`/Alpinas`, `/Suites`, `/Parque`, `/Entorno`).

**Archivos:** `ama/engine/content_strategist.py`, `ama/templates/copy_prompts.yaml`

### RQ-M03: El Distribuidor (Auto-Publisher)
- Instagram Business + Facebook Page → Meta Graph API
- Google Business Profile → posts “Novedades”
- WhatsApp: Status / lista difusión (API Cloud o enlaces + programación n8n)
- Log diario: `ama/logs/publicaciones_YYYY-MM-DD.log`

**Archivos:** `ama/publishers/meta_publisher.py`, `ama/publishers/google_business.py`

### RQ-M04: Multimedia low-cost
- **MoviePy** (open source): slideshow fotos + texto oferta + música libre derechos (biblioteca local)
- **Canva** (manual): plantillas QR y cartelería — AMA genera **brief** y texto, dueño exporta gratis.
- Si falta asset: tarea en tablero *“Misión dueño: video neblina en parque hoy”*.

### RQ-M05: Inteligencia de calendario y estacionalidad (Módulo E)
| Ventana | Acción automática |
|---------|-------------------|
| Oct–Nov | Preventa verano + julio siguiente |
| −60 días feriado puente | Campaña “escapada express” |
| −30 días con huecos | Last minute −15/20% |
| Navidad / Año Nuevo / Carnaval | Paquete estadía mínima 3–4 noches |
| Temporada baja | 4×3, workation, retiros, “lunes a jueves” |
| Martes sin reservas finde | Promo relámpago Lofts parejas |

**Archivos:** `ama/engine/season_planner.py`

### RQ-M06: Atención consultas (tono humano)
- Integración: calendario PMS en tiempo real.
- Si fecha libre → cotización + link MP / seña.
- Si ocupado → alternativas fechas + captura lead.
- Escalamiento a humano si detecta queja o caso complejo.

**Archivos:** `ama/chat/responder.py` (reglas + LLM opcional)

### RQ-M07: Landing dinámica
- Encabezado web cambia según campaña activa (deportivo / parejas / familia).
- Carrd.co o web propia Astro/Next — **prioridad web propia** para SEO y reserva sin comisión.

### RQ-M08: Revenue — precios dinámicos
Factores:
1. Ocupación complejo (%)
2. Magnitud evento provincial
3. Benchmark competencia Bialet (scraping liviano V2)
4. **Gap filler:** 1–2 noches hueco → oferta agresiva auto-publicada

**Archivos:** `ama/engine/revenue_optimizer.py` → escribe en `pricing_engine`

### RQ-M09: Coherencia stock marketing
- Si unidad vendida en Booking → AMA **pausa** ads/posts esa unidad ese finde.
- Trigger desde PMS vía webhook interno.

### RQ-M10: Tablero de Control (Dashboard)
**Stack sugerido:** Streamlit (Python, gratis) o página en `frontend/pages/dashboard_ama.html`

**Widgets:**
- Publicaciones hoy / programadas
- Alertas eventos nuevos
- Selector modo 🟢/🟡
- Cuadro “Acción inmediata”
- Misión para el dueño (contenido faltante)
- KPIs: consultas, conversión, ocupación 30 días

---

## 6. PROTOCOLO COMUNICACIONAL (SOP) — ANTES / DURANTE / DESPUÉS

### 6.1 Antes de la estadía
1. Confirmación reserva + comprobante.
2. Email/WhatsApp con políticas (mascotas, ruido, fogón, depósito).
3. T−24 h: mapa, acceso, WiFi, estacionamiento, **QR guía local**.
4. Sugerencias personalizadas según eventos del finde (AMA).

### 6.2 Durante la estadía
- QR en cabaña (imprimir A4 plastificado — costo mínimo):
  - Reglas de la casa
  - WiFi
  - Guía *“Recomendados Terra Natura”* (comer, paseos, río, Dique)
  - Contacto WhatsApp dueños (solo urgencias)
- Buenas prácticas turísticas sin costo: separación residuos, cuidado agua, silencio nocturno, fogón supervisado.

### 6.3 Después de la estadía
- T+48 h: agradecimiento + link Google Maps.
- Incentivo reseña: descuento próxima estadía (definir % en `REGLAS_NEGOCIO.md`).
- Alta en lista “huéspedes fieles” para ofertas AMA.

### 6.4 Contenido de guía local (base fija — AMA enriquece)
- **Comer:** locales Bialet Massé (actualizar con input dueño).
- **Visitar:** Dique San Roque, paseos río, Cosquín, Carlos Paz según temporada.
- **Actividades:** trekking, cabalgatas, proveedores confiables.

---

## 7. INNOVACIONES LOW-COST (CHECKLIST IMPLEMENTABLE)

| Innovación | Costo | Herramienta |
|------------|-------|-------------|
| QR guía + reglas | ~$0 | Canva free + Google Drive PDF + generador QR Python `qrcode` |
| Cartelería interna | ~$0 | Brief AMA → Canva |
| iCal channel sync | $0 | Airbnb/Booking export + PMS |
| Google Business web | $0 | Perfil completo + posts AMA |
| Email transaccional | $0 | Brevo 300/día |
| Automatización flujos | $0 | n8n self-hosted o GitHub Actions |
| Fotos organizadas | $0 | Drive carpetas §12 |
| Publicidad pago | Variable | Meta Ads — AMA genera creativos; dueño define presupuesto |
| Dominio + SSL | Bajo | Cloudflare + Oracle Free VM |

---

## 8. STACK TECNOLÓGICO UNIFICADO (GRATIS / FREEMIUM)

| Capa | Elección |
|------|----------|
| **PMS Backend** | Python 3.11+ · FastAPI · SQLAlchemy · PostgreSQL |
| **AMA** | Python modules en monorepo `ama/` |
| **Dashboard** | Streamlit o React en `frontend/` |
| **Web pública** | Astro o Vite+React (rápida, SEO) — alternativa MVP: HTML+Bootstrap |
| **Automatización** | n8n (VM) + APScheduler |
| **IA redacción** | API OpenAI/Claude **solo si hay key** — fallback plantillas Jinja2 sin costo |
| **Scraping** | `httpx` + `BeautifulSoup` + calendario feriados JSON local |
| **Video** | MoviePy |
| **Pagos** | Mercado Pago |
| **Storage media** | Google Drive API (fotos dueño) + Supabase Storage (uploads huéspedes) |
| **CI/CD** | GitHub Actions |
| **Hosting** | Oracle Cloud Free Tier (patrón Don Bosco) |
| **Monitoreo** | Uptime Kuma + logs rotativos |

**Evitar en MVP:** Make.com/Zapier de pago, channel manager premium, GPT masivo sin límite, SMS.

---

## 9. ESTRUCTURA DEL REPOSITORIO

```
terra-natura/
├── AGENTS.md                 # Este archivo — leer primero
├── docs/
│   ├── REGLAS_NEGOCIO.md     # ⚠️ Completar con dueño
│   ├── ARQUITECTURA.md
│   ├── API.md
│   ├── GUIA_LOCAL_HUESPED.md # Base QR
│   └── COPY_TONO_MARCA.md
├── backend/                  # PMS FastAPI
│   ├── models/
│   ├── services/
│   │   ├── pricing_engine.py
│   │   ├── disponibilidad_service.py
│   │   └── channel_ical_sync.py
│   ├── routes/
│   ├── jobs/
│   └── app.py
├── ama/                      # Agente Marketing Autónomo
│   ├── scrapers/
│   ├── engine/
│   │   ├── content_strategist.py
│   │   ├── season_planner.py
│   │   └── revenue_optimizer.py
│   ├── publishers/
│   ├── chat/
│   ├── templates/
│   └── logs/
├── frontend/
│   ├── public/               # Web reservas
│   └── pages/                # Panel staff + AMA
├── automation/
│   └── n8n/
├── archivos multimedia/    # Fotos/videos clasificadas (dueño); inventario: docs/MEDIA_INVENTARIO.md
├── assets/
│   └── qr/                   # Generados
├── database/
├── local/
│   ├── publicar-desde-config.ps1
│   └── config-publicacion.json.example
├── tests/
└── .env.example
```

---

## 10. CONTENIDO QUE DEBÉS AGREGAR DENTRO DEL AGENTE (ARCHIVOS AUXILIARES)

El `AGENTS.md` es la constitución; estos archivos son la **memoria operativa** que el agente debe leer según tarea:

| Archivo | Contenido obligatorio |
|---------|----------------------|
| `docs/REGLAS_NEGOCIO.md` | % seña, cancelación, check-in/out, depósito, mascotas, fogón, ruido, estacionamiento |
| `docs/COPY_TONO_MARCA.md` | Ejemplos buenos/malos de mensajes, palabras prohibidas, firma |
| `docs/UNIDADES.md` | Ficha de las **5** unidades + amenities + fotos clave |
| `docs/MEDIA_INVENTARIO.md` | Rutas locales `archivos multimedia/` · uso web/redes/AMA |
| `docs/GUIA_LOCAL_HUESPED.md` | Restaurantes, paseos, emergencias, proveedores |
| `docs/SEGURIDAD_CREDENCIALES.md` | Drive/API sin contraseñas en repo |
| `ama/templates/copy_prompts.yaml` | Prompts por tipo campaña |
| `ama/data/feriados_ar.json` | Calendario feriados actualizado |
| `ama/data/grupos_fb.json` | URLs grupos segmentados (running, turismo Punilla, etc.) |
| `.env` (no commitear) | Tokens Meta, Google, MP, WhatsApp, opcional OPENAI_API_KEY |

---

## 11. ORGANIZACIÓN GOOGLE DRIVE (REQUISITO PREVIO AMA)

```
TerraNatura-Media/
├── Alpinas/
│   ├── exterior_dia/
│   ├── interior_noche/
│   └── matrimonial/
├── Suites/
├── Parque/
├── Entorno_Bialet/
└── Videos_brutos/
```

**Convención nombres:** `alpina_01_living_dia.jpg` — la IA selecciona por keywords.

**Espejo en disco local (repo):** `archivos multimedia/` — inventario y mapeo a unidades en `docs/MEDIA_INVENTARIO.md`.

## 12. TRIGGERS Y ACCIONES DIARIAS (AMA)

| Trigger (cron 08:00 ART) | Acción |
|--------------------------|--------|
| Diario | Scraper eventos → cache |
| Diario | Revisar ocupación 7–14 días → si baja, plan promo |
| Lunes | Calendario contenido semana + modo automático/aprobación |
| −60 d feriado | Campaña puente |
| Post publicado | Escribir log + métricas si API lo permite |
| Reserva confirmada PMS | Pausar creativos esa unidad/fecha |
| Pago MP webhook | Enviar pack bienvenida |

**Acción inmediata (tablero):**  
Input dueño → buscar assets Drive → generar copy → preview → publicar APIs.

---

## 13. PROMOCIONES TEMPORADA BAJA (AUTOMATIZABLES)

Prioridad de implementación (dueño elige peso en `REGLAS_NEGOCIO.md`):
1. **4×3** noches en días de semana.
2. **Workation** −20% estadía ≥7 noches lun–jue.
3. **Pack bienvenida** (fiambres regionales) — costo bajo, copy premium.
4. **Retiro bienestar** — bloqueo 3–5 unidades, precio paquete.
5. **Gap filler** — 1–2 noches entre reservas, −25% auto.

---

## 14. REGLAS PARA EL AGENTE DESARROLLADOR (CURSOR)

1. No confirmar reserva sin pasar por `disponibilidad_service`.
2. Precios solo vía `pricing_engine` / `revenue_optimizer`.
3. Toda publicación AMA debe quedar en log auditable.
4. Modo 🟡 por defecto hasta validar calidad copy (primer mes).
5. Español Argentina, fechas DD/MM/YYYY, ARS.
6. Commits solo si el dueño lo pide.
7. Priorizar código open source; documentar cualquier servicio de pago nuevo.
8. Paridad operativa con proyecto Don Bosco en scripts `local/`.

---

## 15. PUBLICACIÓN EN SERVIDOR

- Ruta sugerida: `/var/lib/terra-natura/`
- Script: `local/publicar-desde-config.ps1` (crear desde Don Bosco cuando exista VM)
- Nunca commitear `.pem`, `.env`, tokens Meta/Google.

---

## 16. ESTADO ACTUAL Y PRÓXIMOS PASOS

| Item | Estado |
|------|--------|
| AGENTS.md (constitución) | ✅ Este documento |
| Código PMS / AMA | ⬜ Pendiente — iniciar tras pulir reglas |
| `docs/REGLAS_NEGOCIO.md` | ✅ Base completa — pendiente WhatsApp, precios, mascotas |
| `docs/UNIDADES.md` | ✅ 5 unidades con nombres y amenities |
| Drive organizado | ⬜ Requiere dueño |
| Cuentas API (Meta, Google Business, MP) | ⬜ Verificar acceso |

**Orden de desarrollo recomendado al programar:**
1. Seed **5 unidades** desde `docs/UNIDADES.md` + precios en `REGLAS_NEGOCIO.md`  
2. PMS core (RQ-01–06) + iCal  
3. Web reserva directa (RQ-20)  
4. Comunicación WhatsApp/email (RQ-17)  
5. AMA M01–M03 (eventos + contenido + publicar con aprobación)  
6. Revenue + tablero (M08–M10)

---

## 17. REFERENCIAS

- Patrón arquitectónico hermano: `Proyecto Don Bosco/gestion_partidos/AGENTS.md`
- Conversación requisitos: export Gemini → `docs/REGLAS_NEGOCIO.md`

---

*Versión documento: 2.0 — Integración visión marketing autónomo + PMS Terra Natura, Bialet Massé.*
