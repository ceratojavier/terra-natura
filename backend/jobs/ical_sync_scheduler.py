"""
Job periódico — importación iCal Booking/Airbnb cada N minutos.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.config.database import SessionLocal
from backend.config.settings import ICAL_SYNC_INTERVAL_MIN, ICAL_SYNC_ON_STARTUP
from backend.services import channel_ical_sync

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None
_ultimo_sync: dict | None = None


def get_ultimo_sync() -> dict | None:
    return _ultimo_sync


def _ejecutar_sync() -> None:
    global _ultimo_sync
    db = SessionLocal()
    try:
        resultado = channel_ical_sync.sync_todos_los_feeds(db, dry_run=False, notificar=True)
        _ultimo_sync = {
            **resultado,
            "job_en": datetime.now(timezone.utc).isoformat(),
        }
        nuevas = resultado.get("nuevas_total") or 0
        if nuevas:
            logger.info("ical sync: %s reserva(s) nueva(s) importada(s)", nuevas)
    except Exception as e:
        logger.exception("ical sync job falló: %s", e)
        _ultimo_sync = {
            "ok": False,
            "error": str(e),
            "job_en": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()


def iniciar_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    if _scheduler and _scheduler.running:
        return _scheduler

    intervalo = max(5, ICAL_SYNC_INTERVAL_MIN)
    _scheduler = BackgroundScheduler(timezone="America/Argentina/Cordoba")
    _scheduler.add_job(
        _ejecutar_sync,
        trigger=IntervalTrigger(minutes=intervalo),
        id="ical_sync_booking",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("Scheduler iCal activo — cada %s min", intervalo)

    if ICAL_SYNC_ON_STARTUP:
        from datetime import datetime

        _scheduler.add_job(
            _ejecutar_sync,
            trigger="date",
            run_date=datetime.now(),
            id="ical_sync_startup",
            replace_existing=True,
        )

    return _scheduler


def detener_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None
