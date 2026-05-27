"""CLI: python -m backend.services.youtube_turismo_cli"""
from backend.config.database import SessionLocal, init_db
from backend.services.youtube_turismo import recolectar_videos


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        r = recolectar_videos(db)
        print(r)
    finally:
        db.close()


if __name__ == "__main__":
    main()
