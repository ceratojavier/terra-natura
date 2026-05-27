"""
Job semanal — actualiza agenda de eventos hasta marzo del año siguiente.
Ejecutar: python -m backend.jobs.actualizar_agenda_semanal
Programar en Windows: Programador de tareas → lunes 08:00
"""
from __future__ import annotations

from datetime import date


def main() -> None:
    from ama.scrapers.event_hunter import actualizar_agenda

    hoy = date.today()
    anio_marzo = hoy.year + 1 if hoy.month > 3 else hoy.year
    hasta = date(anio_marzo, 3, 31)
    r = actualizar_agenda(desde=hoy, hasta=hasta, db=None, scrape_web=True)
    print(r.get("mensaje", r))


if __name__ == "__main__":
    main()
