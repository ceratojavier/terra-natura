"""PMS contexto para Director Semanal."""
from datetime import date

from ama.engine.pms_contexto import (
    analizar_semana_pms,
    finde_cerca_lleno,
    formatear_ars,
    texto_cotizacion_copy,
)


def test_sin_db_devuelve_desconectado():
    ctx = analizar_semana_pms(date(2026, 6, 1), date(2026, 6, 7), db=None)
    assert ctx["conectado"] is False
    assert ctx["senal"] == "neutro"


def test_finde_lleno_heuristica():
    ctx = {
        "conectado": True,
        "finde_ocupacion_pct": 90,
        "unidades_libres_finde": ["alpina-1"],
        "total_unidades": 5,
    }
    assert finde_cerca_lleno(ctx, date(2026, 6, 5)) is True


def test_formatear_ars():
    assert formatear_ars(120000) == "$120.000"


def test_texto_cotizacion_copy():
    txt = texto_cotizacion_copy(
        {
            "unidad_nombre": "Alpina 1",
            "noches": 2,
            "check_in": "2026-06-05",
            "check_out": "2026-06-07",
            "total_legible": "$200.000",
            "promo_texto": "Promo invierno 5+1 aplicada",
        }
    )
    assert "Alpina 1" in txt
    assert "$200.000" in txt
    assert "5+1" in txt
