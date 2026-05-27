"""
Feed iCal de ocupación por unidad — reservas con estado bloqueante.
DTSTART/DTEND DATE (fin exclusivo), compatible con Airbnb/Booking import.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from backend.models.reserva import ESTADOS_BLOQUEANTES, Reserva


def _fmt_date(d: date) -> str:
    return d.strftime("%Y%m%d")


def _escape_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def _prop(name: str, value: str) -> str:
    return f"{name}:{_escape_text(value)}"


def generar_ics_ocupacion(
    db: Session,
    unidad_id: str,
    *,
    nombre_unidad: str,
    nombre_calendario: str | None = None,
    host_uid_domain: str = "pms.terra-natura.local",
) -> str:
    rows = (
        db.query(Reserva)
        .filter(
            Reserva.unidad_id == unidad_id,
            Reserva.estado.in_(ESTADOS_BLOQUEANTES),
        )
        .order_by(Reserva.check_in.asc(), Reserva.id.asc())
        .all()
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    calname = nombre_calendario or f"Terra Natura — {nombre_unidad}"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "PRODID:-//Terra Natura//PMS//ES",
        _prop("X-WR-CALNAME", calname),
        _prop("X-WR-CALDESC", f"Ocupación {nombre_unidad}"),
    ]

    for r in rows:
        summary = f"Ocupado — {nombre_unidad} ({r.estado})"
        desc = f"PMS Terra Natura. Estado={r.estado} origen={r.origen}"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{r.id}@{host_uid_domain}",
                f"DTSTAMP:{stamp}",
                "SEQUENCE:0",
                f"DTSTART;VALUE=DATE:{_fmt_date(r.check_in)}",
                f"DTEND;VALUE=DATE:{_fmt_date(r.check_out)}",
                "TRANSP:OPAQUE",
                _prop("SUMMARY", summary),
                _prop("DESCRIPTION", desc),
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
