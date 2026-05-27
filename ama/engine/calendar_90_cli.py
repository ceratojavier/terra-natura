"""CLI: python -m ama.engine.calendar_90_cli"""
from __future__ import annotations

from datetime import date

from backend.config.database import SessionLocal, init_db
from backend.services.ama_service import generar_calendario_90_api


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        r = generar_calendario_90_api(
            date.today(),
            90,
            guardar=True,
            reemplazar_borradores=False,
            db=db,
        )
        print("Nota: videos con B-roll requieren yt-dlp + ffmpeg")
        res = r.get("resumen", {})
        print("OK guardadas:", r.get("guardadas"), "total plan:", res.get("total"))
        print("por_canal:", res.get("por_canal"))
        print("por_objetivo:", res.get("por_objetivo"))
        print("export:", r.get("export_json"))
    finally:
        db.close()


if __name__ == "__main__":
    main()
