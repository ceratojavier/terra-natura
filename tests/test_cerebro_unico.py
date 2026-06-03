"""Cerebro único — Director Semanal delegación."""
from datetime import date

from ama.engine.director_semanal import planificar_semana
from ama.engine.ejecutar_director import mensaje_legacy_deprecado
from ama.engine.estratega_dia import planificar_dia, pieza_director_en_fecha


def test_estratega_delega_al_director():
    ref = date(2026, 6, 2)
    pieza = pieza_director_en_fecha(ref)
    dia = planificar_dia(ref)
    assert dia.get("delegado_director") is True
    if pieza:
        assert dia.get("sin_pieza") is False
        assert dia.get("pieza_id") == pieza.get("pieza_id")
    else:
        assert dia.get("sin_pieza") is True


def test_legacy_deprecado_mensaje():
    r = mensaje_legacy_deprecado("POST /ejecutar")
    assert r["deprecated"] is True
    assert "Director" in r["mensaje"]
