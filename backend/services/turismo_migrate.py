"""Migración ligera SQLite — columnas YouTube en turismo_contenidos."""
from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

_COLS = (
    ("youtube_id", "VARCHAR(20)"),
    ("thumbnail_url", "VARCHAR(500)"),
    ("duracion_segundos", "INTEGER"),
    ("vistas", "INTEGER"),
    ("publicado_en", "DATETIME"),
)


def migrate_turismo_youtube(engine: Engine) -> None:
    insp = inspect(engine)
    if "turismo_contenidos" not in insp.get_table_names():
        return
    existing = {c["name"] for c in insp.get_columns("turismo_contenidos")}
    with engine.begin() as conn:
        for name, typ in _COLS:
            if name not in existing:
                conn.execute(text(f"ALTER TABLE turismo_contenidos ADD COLUMN {name} {typ}"))
