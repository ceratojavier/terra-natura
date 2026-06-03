"""Coherencia calendario estratégico 2026 — efemérides no se mezclan."""
from datetime import date

from ama.engine.estrategia_marketing_anual import (
    efemeride_prioritaria_en_fecha,
    pieza_editorial_para_fecha,
    validar_copy_efemeride,
    _init_editorial_pools,
    _EDITORIAL_POR_MES,
)


def test_junio_18_es_campana_padre_no_nino():
    d = date(2026, 6, 18)
    e, dias = efemeride_prioritaria_en_fecha(d)
    assert e is not None
    assert e["slug"] == "dia_padre"
    assert dias == 3
    pieza = pieza_editorial_para_fecha(d)
    assert "niño" not in pieza["titulo"].lower()
    assert "padre" in pieza["titulo"].lower() or "papá" in pieza["titulo"].lower()


def test_agosto_13_campana_nino_no_padre():
    d = date(2026, 8, 13)
    e, dias = efemeride_prioritaria_en_fecha(d)
    assert e is not None
    assert e["slug"] == "dia_nino"
    pieza = pieza_editorial_para_fecha(d)
    assert "padre" not in pieza["titulo"].lower()
    assert "papá" not in pieza["titulo"].lower()


def test_validar_prohibido_padre_menciona_nino():
    avisos = validar_copy_efemeride("Día del Padre (AR)", "Feliz día del niño en agosto")
    assert len(avisos) >= 1


def test_doce_meses_editorial_sin_plantilla_generica():
    _init_editorial_pools()
    assert len(_EDITORIAL_POR_MES) == 12
    for m in range(1, 13):
        pool = _EDITORIAL_POR_MES[m]
        assert len(pool) >= 28
        titulos = [p["titulo"] for p in pool]
        assert not any("escapada a las sierras sin apuro" in t and "mes" in t for t in titulos)
