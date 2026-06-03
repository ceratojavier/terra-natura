"""Cerebro único canal/formato — coherencia grilla vs campaña."""
from datetime import date

from ama.engine.piezas_editoriales import listar_piezas_editoriales
from ama.engine.publicacion_medio import decidir_publicacion
from ama.engine.plan_marketing_unificado import _piezas_para_hito


def test_domingo_editorial_es_whatsapp_status():
    d = date(2026, 6, 7)  # domingo
    medio = decidir_publicacion(
        tipo_pieza="emocional_tema",
        fecha=d,
        titulo="Vínculo con huéspedes",
        es_editorial=True,
    )
    assert medio["canal"] == "whatsapp"
    assert medio["formato"] == "status"
    assert medio["justificacion_medio"]


def test_t_post_cierre_whatsapp():
    medio = decidir_publicacion(
        tipo_pieza="emocional_tema",
        fecha=date(2026, 6, 23),
        titulo="Gracias por elegirnos",
        ventana="t_post",
        hito_tipo="finde_largo",
    )
    assert medio["canal"] == "whatsapp"
    assert medio["formato"] == "status"


def test_promo_t7_reel_instagram():
    medio = decidir_publicacion(
        tipo_pieza="promo_cta",
        fecha=date(2026, 6, 14),
        titulo="Reservá tu lugar",
        ventana="t7",
        hito_tipo="finde_largo",
        dias_antes=7,
    )
    assert medio["canal"] == "instagram"
    assert medio["formato"] == "reel"


def test_lunes_editorial_post():
    d = date(2026, 6, 1)  # lunes
    piezas = listar_piezas_editoriales(d, d)
    assert len(piezas) == 1
    assert piezas[0]["canal"] == "instagram"
    assert piezas[0]["formato"] == "post"
    assert piezas[0].get("justificacion_medio")


def test_hito_piezas_tienen_justificacion():
    item = {
        "nombre": "Finde Largo Junio",
        "tipo": "finde_largo",
        "fecha_inicio": "2026-06-20",
    }
    piezas = _piezas_para_hito(item, date(2026, 5, 1), "test-hito")
    assert piezas
    post = next(p for p in piezas if p.get("ventana") == "t_post")
    assert post["canal"] == "whatsapp"
    assert post.get("justificacion_medio")
