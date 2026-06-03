"""Director Semanal — cantidad variable y sin editorial diario."""
from datetime import date

from ama.engine.director_semanal import (
    fin_semana,
    inicio_semana,
    planificar_semana,
    piezas_calendario_rango,
)


def test_semana_tiene_inicio_lunes():
    d = date(2026, 6, 4)  # jueves
    assert inicio_semana(d) == date(2026, 6, 1)
    assert fin_semana(d) == date(2026, 6, 7)


def test_plan_semanal_cantidad_razonable():
    plan = planificar_semana(date(2026, 6, 2))
    assert plan["total_piezas"] <= 9
    assert "narrativa" in plan
    assert "contexto_pms" in plan
    assert plan["narrativa"]


def test_editorial_max_3_en_semana_quieta():
    plan = planificar_semana(date(2026, 5, 5))
    assert plan["total_editorial"] <= 3


def test_calendario_rango_deduplica():
    desde = date(2026, 6, 1)
    hasta = date(2026, 6, 30)
    piezas = piezas_calendario_rango(desde, hasta)
    ids = [p["pieza_id"] for p in piezas]
    assert len(ids) == len(set(ids))
