"""
Contexto de viaje en fines de semana largos — días del puente y audiencia por origen.
Córdoba capital puede salir viernes a la noche; Buenos Aires suele llegar sábado a la mañana.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

_DIAS_ES = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)

_ORIGENES_VIAJERO: list[dict[str, Any]] = [
    {
        "id": "cordoba_capital",
        "nombre": "Córdoba capital / Gran Córdoba",
        "distancia_km_bialet": 55,
        "salida_laboral": "Viernes al terminar el trabajo (18–20 h)",
        "primera_noche_alojamiento": "viernes",
        "noches_tipicas_puente_4d": 3,
        "publico_copy": "Salís el viernes y dormís esa noche en el Valle — sin perder el finde.",
        "canales_prioridad": ["instagram", "facebook", "whatsapp_status"],
    },
    {
        "id": "interior_cordoba",
        "nombre": "Interior Córdoba (≤2 h a Bialet)",
        "distancia_km_bialet": 40,
        "salida_laboral": "Viernes tarde o sábado temprano",
        "primera_noche_alojamiento": "viernes",
        "noches_tipicas_puente_4d": 2,
        "publico_copy": "Escapada corta en auto — pileta y parque el mismo finde.",
        "canales_prioridad": ["instagram", "whatsapp_status"],
    },
    {
        "id": "buenos_aires",
        "nombre": "Buenos Aires / AMBA / La Plata",
        "distancia_km_bialet": 750,
        "salida_laboral": "Viernes noche o sábado muy temprano (micro/auto 7–9 h)",
        "primera_noche_alojamiento": "sabado",
        "noches_tipicas_puente_4d": 2,
        "publico_copy": "Si salís el viernes a la noche, llegás de madrugada: mejor reservar desde el sábado y aprovechar 2–3 noches.",
        "canales_prioridad": ["instagram", "facebook"],
        "nota_operativa": "Promover check-in sábado AM y estadía hasta lunes o martes según feriado.",
    },
    {
        "id": "rosario_santa_fe",
        "nombre": "Rosario / Santa Fe / Entre Ríos",
        "distancia_km_bialet": 500,
        "salida_laboral": "Viernes tarde o sábado madrugada",
        "primera_noche_alojamiento": "sabado",
        "noches_tipicas_puente_4d": 2,
        "publico_copy": "Puente ideal con llegada sábado al mediodía — menos desgaste que BA.",
        "canales_prioridad": ["instagram", "facebook"],
    },
    {
        "id": "mendoza_norte",
        "nombre": "Mendoza / San Juan / Norte",
        "distancia_km_bialet": 450,
        "salida_laboral": "Jueves noche o viernes temprano en feriados largos",
        "primera_noche_alojamiento": "viernes",
        "noches_tipicas_puente_4d": 3,
        "publico_copy": "En puentes de 4 días conviene salir jueves o viernes AM para no perder noches.",
        "canales_prioridad": ["instagram"],
    },
]


def _dia_semana(d: date) -> str:
    return _DIAS_ES[d.weekday()]


def desglose_dias_puente(fecha_inicio: date, fecha_fin: date) -> list[dict]:
    out = []
    d = fecha_inicio
    while d <= fecha_fin:
        out.append(
            {
                "fecha": d.isoformat(),
                "dia_semana": _dia_semana(d),
                "dia_numero": d.weekday(),
            }
        )
        d += timedelta(days=1)
    return out


def enriquecer_finde_largo(puente: dict, feriados_iso: set[str] | None = None) -> dict:
    """
    Agrega cantidad de días, lista viernes–lunes, feriados incluidos y audiencias por origen.
    """
    ini = date.fromisoformat(puente["fecha_inicio"][:10])
    fin = date.fromisoformat(puente["fecha_fin"][:10])
    dias = desglose_dias_puente(ini, fin)
    feriados = feriados_iso or set()
    for d in dias:
        d["es_feriado_nacional"] = d["fecha"] in feriados

    nombres_unicos = []
    for d in dias:
        if d["dia_semana"] not in nombres_unicos:
            nombres_unicos.append(d["dia_semana"])

    cantidad = len(dias)
    noches = max(cantidad - 1, puente.get("noches_sugeridas") or 1)

    audiencias = []
    for orig in _ORIGENES_VIAJERO:
        primera = orig["primera_noche_alojamiento"]
        idx_primera = next(
            (i for i, d in enumerate(dias) if d["dia_semana"] == primera),
            0,
        )
        noches_recom = max(1, cantidad - idx_primera)
        if cantidad >= 4 and orig["id"] == "buenos_aires":
            noches_recom = min(noches_recom, 3)
        audiencias.append(
            {
                "origen_id": orig["id"],
                "origen": orig["nombre"],
                "salida_desde_trabajo": orig["salida_laboral"],
                "check_in_sugerido": dias[idx_primera]["dia_semana"]
                if idx_primera < len(dias)
                else primera,
                "check_out_sugerido": dias[-1]["dia_semana"],
                "noches_recomendadas": noches_recom,
                "copy_segmento": orig["publico_copy"],
                "canales": orig.get("canales_prioridad", []),
            }
        )

    return {
        **puente,
        "cantidad_dias": cantidad,
        "cantidad_noches": noches,
        "dias_calendario": dias,
        "dias_texto": " · ".join(nombres_unicos),
        "incluye_viernes": any(d["dia_numero"] == 4 for d in dias),
        "incluye_lunes": any(d["dia_numero"] == 0 for d in dias),
        "audiencias_origen": audiencias,
        "segmentacion_principal": _segmento_principal(cantidad, dias),
    }


def _segmento_principal(cantidad: int, dias: list[dict]) -> str:
    if cantidad >= 4:
        return "puente_4_dias"
    if cantidad == 3:
        return "finde_largo_3_dias"
    return "escapada_corta"


def feriados_en_set(feriados: list[dict]) -> set[str]:
    return {f["fecha"][:10] for f in feriados if f.get("fecha")}
