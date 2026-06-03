"""Sync iCal Booking + alertas + WhatsApp parse."""
from datetime import date

from backend.services.channel_ical_sync import parse_ical_events
from backend.services.whatsapp_cloud_service import extraer_mensajes_entrantes


def test_parse_ical_evento_booking():
    ics = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:booking-12345@booking.com
DTSTART;VALUE=DATE:20260615
DTEND;VALUE=DATE:20260618
SUMMARY:Closed - Guest Name
END:VEVENT
END:VCALENDAR"""
    ev = parse_ical_events(ics)
    assert len(ev) == 1
    assert ev[0]["uid"] == "booking-12345@booking.com"
    assert ev[0]["check_in"] == date(2026, 6, 15)
    assert ev[0]["check_out"] == date(2026, 6, 18)


def test_whatsapp_extraer_mensaje():
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "5493512345678",
                                    "id": "wamid.x",
                                    "type": "text",
                                    "text": {"body": "Hola, precio para el 10/7 al 12/7"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    msgs = extraer_mensajes_entrantes(payload)
    assert len(msgs) == 1
    assert msgs[0]["from"] == "5493512345678"
    assert "precio" in msgs[0]["text"]
