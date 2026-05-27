# Arquitectura multi-agente — Terra Natura

## Visión

Tres agentes especializados + orquestador, sobre el mismo PMS (FastAPI + SQLite/PostgreSQL).

```
                    ┌─────────────────────┐
                    │   Orquestador       │
                    │   (ciclo diario)    │
                    └──────────┬──────────┘
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
   │   CHANNELS    │   │     CRM       │   │   CONTENT     │
   │ Channel Mgr   │   │ Comunicación  │   │ Redes / AMA   │
   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
           │                   │                   │
           ▼                   ▼                   ▼
      Reservas + iCal      Leads + plantillas   Calendario AMA
```

## Agentes

| ID | Nombre | Responsabilidad |
|----|--------|-----------------|
| `channels` | Channel Manager | iCal export, modo OTAs, ocupación 7d, conflictos |
| `crm` | CRM & Comunicación | Leads, mensajes pre/durante/post, inbox pendientes |
| `content` | Contenido & Redes | Calendario editorial, copy, alertas feriados (AMA) |

## Rutas API

- `GET /api/agentes/hub` — dashboard
- `POST /api/agentes/ciclo-diario` — ejecuta los 3
- `POST /api/agentes/{id}/ejecutar` — un agente
- `GET /api/agentes/crm/leads` — leads
- `GET /api/agentes/crm/reservas/{id}/mensajes` — borradores WhatsApp

## Panel web

`http://localhost:8000/agentes` (con servidor levantado)

## Automatización

- Script: `automation/run_daily_agents.py`
- Windows: `local/Ejecutar-agentes-diario.bat`
- Programar en Programador de tareas (08:00 ART)

## Próximas fases

1. **Channels:** import iCal desde Airbnb/Booking (anti overbooking bidireccional)
2. **CRM:** webhook WhatsApp Cloud API, envío automático con aprobación
3. **Content:** publicación Meta Graph API (modo 🟢/🟡)
4. **Jobs:** APScheduler dentro del backend

## Carpetas

```
agents/
  core/          # base, registry, orchestrator
  content/       # AMA
  crm/           # leads + plantillas
  channels/      # calendario multicanal
  data/logs/     # ciclos JSONL
```
