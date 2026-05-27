# Dónde busca el agente de eventos (Terra Natura)

Objetivo: **no** llenar el calendario con feriados de Google ni títulos sin fecha. Solo fechas con **día confirmado** que puedan generar **estadía en Bialet Massé** (Valle de Punilla, Dique San Roque, excursión a Córdoba/Kempes ~40–55 km).

## Fuente principal (la que pediste)

| Qué | URL | Cómo se lee | Filtro Bialet |
|-----|-----|-------------|---------------|
| **Córdoba Turismo — agenda oficial** | https://cordobaturismo.gov.ar/agenda/ | API WordPress *The Events Calendar*: `https://cordobaturismo.gov.ar/wp-json/tribe/events/v1/events` (paginado, `start_date` / `end_date`) | `ama/engine/evento_relevancia_bialet.py` + `ama/data/criterios_eventos_cabanas.json` |
| Código | `ama/scrapers/sources_cordoba_turismo.py` | | |
| Auditoría | `ama/data/eventos_cordoba_turismo_auditoria.json` | relevantes + muestra de descartados | |

**Importante:** el sitio suele devolver **403** a scripts Python (WAF). En el navegador la API sí responde (~590 eventos en sync completo). Por eso existe:

- Sync local: `ama/data/eventos_cordoba_turismo_sync.json`
- Guía sync: `docs/SYNC_CORDOBA_TURISMO.md`
- Opcional: `playwright install` + `py -m ama.scrapers.sources_cordoba_turismo --playwright`

## Fuentes ya en el sistema (JSON / seed)

| Fuente | Archivo / módulo | Uso |
|--------|------------------|-----|
| Feriados y puentes AR | `ama/data/feriados_puentes_ar.json` | Finde largo, campaña puente |
| Eventos masivos confirmados | `ama/data/eventos_confirmados_ar.json` | Feria Córdoba, Kempes, Cosquín, etc. |
| Calendario importante | `ama/data/calendario_importante_ar.json` | Bialet, Oktoberfest, referencias |
| Fiestas recurrentes | `ama/data/fiestas_recurrentes_extendido.json` | Ventanas estacionales |
| Seed turismo | `backend/services/turismo_seed_data.py` | Grilla base |

## Fuentes documentadas — scraper pendiente

Listadas en `ama/data/fuentes_agenda_eventos.json` (medios, deportes, recitales). Próxima prioridad Punilla:

- Bialet Massé: https://bialetmasse.com.ar/eventos/
- Carlos Paz / Cosquín: medios y sitios de festival (ver JSON)

## Qué NO entra al calendario “confirmado”

- Títulos scrapeados **sin fecha** (`titulo_web_sin_fecha`)
- Localidades lejanas (Río Cuarto, Villa María, etc.) — ver exclusiones en criterios
- Eventos Córdoba Turismo **sin** `potencial_cabaña` (quedan en auditoría como descartados)

## Actualizar en tu PC

1. Doble clic: `local/Actualizar-agenda-eventos.bat` (fusiona cache semanal)
2. Si Córdoba da 403: seguir `docs/SYNC_CORDOBA_TURISMO.md` y volver a ejecutar (1)
3. Programa web: `http://127.0.0.1:8000/programa` → agenda usa `backend/services/calendario_importante_service.py`

## Respuesta API

En `GET /api/calendario/importante` el bloque `agente_eventos.cordoba_turismo` indica método (`api_httpx`, `sync_local`, `playwright`), totales bruto/relevantes y error si hubo 403.
