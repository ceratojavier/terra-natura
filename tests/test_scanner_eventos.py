"""Scanner de eventos — aviso manual y bandeja."""
from datetime import date

from ama.engine.scanner_eventos import (
    _extraer_evento_desde_texto,
    _parsear_fecha_texto,
    analizar_oportunidad,
    analizar_texto_dueño,
    descartar_evento,
    incorporar_evento,
    listar_bandeja,
    registrar_aviso,
)


def test_parsea_miercoles_que_viene():
    ref = date(2026, 6, 2)  # martes
    fd = _parsear_fecha_texto("el miércoles que viene", ref=ref)
    assert fd == date(2026, 6, 3)


def test_extrae_central_boca_kempes():
    ref = date(2026, 6, 2)
    ev = _extraer_evento_desde_texto(
        "central boca en el kempes el miercoles que viene",
        ref=ref,
    )
    assert "Central" in ev["nombre"] and "Boca" in ev["nombre"]
    assert ev["categoria"] == "futbol"
    assert ev["fecha_inicio"] == "2026-06-03"
    assert "Kempes" in ev["localidad"]


def test_analisis_futbol_corto_plazo():
    ref = date(2026, 6, 2)
    ev = _extraer_evento_desde_texto(
        "Central vs Boca Kempes miércoles que viene",
        ref=ref,
    )
    an = analizar_oportunidad(ev, ref=ref)
    assert an["relevante"] is True
    assert an["veredicto"] in ("si_corto_plazo", "si_radar", "revisar")
    assert an["producir_ahora"] is False
    assert len(an["sugerencias_tacticas"]) >= 1


def test_analizar_texto_sin_guardar():
    r = analizar_texto_dueño("Central Boca Kempes el miércoles que viene", guardar=False)
    assert "analisis" in r
    assert r["guardado"] is False


def test_registrar_e_incorporar(tmp_path, monkeypatch):
    import ama.engine.scanner_eventos as se

    bandeja = tmp_path / "bandeja.json"
    conf = tmp_path / "confirmados.json"
    bandeja.write_text('{"items":[]}', encoding="utf-8")
    conf.write_text('{"eventos":[]}', encoding="utf-8")
    monkeypatch.setattr(se, "_BANDEJA", bandeja)
    monkeypatch.setattr(se, "_CONFIRMADOS", conf)

    ref = date(2026, 6, 2)
    r = registrar_aviso("Central Boca Kempes miércoles que viene", ref=ref, forzar=True)
    assert r["ok"] is True
    item_id = r["item"]["id"]

    inc = incorporar_evento(item_id)
    assert inc["ok"] is True

    conf_data = __import__("json").loads(conf.read_text(encoding="utf-8"))
    assert len(conf_data["eventos"]) == 1

    desc = descartar_evento("no-existe")
    assert desc["ok"] is False


def test_listar_bandeja_vacia():
    data = listar_bandeja()
    assert "total_pendientes" in data
    assert "items" in data
