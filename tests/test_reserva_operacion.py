"""Reserva operación manual (panel móvil)."""
from datetime import date, timedelta

from backend.services.reserva_service import codigo_reserva_amigable


def test_codigo_reserva_formato():
    c = codigo_reserva_amigable("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    assert c.startswith("TN-")
    assert len(c) == 11


def test_crear_operacion_requiere_db():
    """Smoke: import del servicio sin levantar DB."""
    from backend.services import reserva_service

    assert hasattr(reserva_service, "crear_operacion")
