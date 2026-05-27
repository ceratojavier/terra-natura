"""
Orquestador — ejecuta agentes en orden y registra el ciclo diario.
Orden: Canales → CRM → Contenido (contenido usa estado de ocupación).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.core.base import AgentStatus, AgentRunResult
from agents.core.registry import AGENT_REGISTRY

LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "logs"
CYCLE_ORDER = ("channels", "calendar", "crm", "content")


def run_agent(
    agent_id: str,
    db: Any | None = None,
    *,
    task_ids: list[str] | None = None,
) -> AgentRunResult:
    agent = AGENT_REGISTRY[agent_id]
    return agent.ejecutar(db, task_ids=task_ids)


def run_daily_cycle(db: Any | None = None) -> dict:
    """Ciclo completo para cron / panel."""
    resultados: list[dict] = []
    alertas_globales: list[str] = []

    for aid in CYCLE_ORDER:
        if aid not in AGENT_REGISTRY:
            continue
        r = run_agent(aid, db)
        resultados.append(r.to_dict())
        alertas_globales.extend(
            [f"[{r.nombre}] {a}" for a in r.alertas]
        )

    payload = {
        "tipo": "ciclo_diario",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agentes": resultados,
        "alertas": alertas_globales,
        "ok": all(x["status"] in ("ok", "warning") for x in resultados),
    }
    _log_cycle(payload)
    return payload


def _log_cycle(payload: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = LOG_DIR / f"ciclo_{day}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def ultimo_ciclo() -> dict | None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(LOG_DIR.glob("ciclo_*.jsonl"), reverse=True)
    if not files:
        return None
    line = ""
    with files[0].open(encoding="utf-8") as f:
        for line in f:
            pass
    if not line.strip():
        return None
    return json.loads(line)
