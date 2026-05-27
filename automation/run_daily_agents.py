"""
Cron diario — ejecuta los 3 agentes Terra Natura.
python automation/run_daily_agents.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.config.database import SessionLocal, init_db
from agents.core.orchestrator import run_daily_cycle


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        result = run_daily_cycle(db)
        print("Ciclo OK:", result.get("ok"))
        for a in result.get("alertas", []):
            print(" -", a)
    finally:
        db.close()


if __name__ == "__main__":
    main()
