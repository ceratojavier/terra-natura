"""API de agentes Terra Natura."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from agents.core.orchestrator import run_agent, run_daily_cycle, ultimo_ciclo
from agents.core.registry import list_agents_meta
from agents.crm import store
from agents.crm.templates import sugerir_para_reserva
from backend.services import reserva_service


def hub_dashboard(db: Session) -> dict:
    from backend.services import ama_service

    meta = list_agents_meta()
    ultimo = ultimo_ciclo()
    leads = store.list_leads()
    reservas = reserva_service.listar(db, None, None, None)
    activas = [r for r in reservas if r.get("estado") not in ("cerrada", "cancelada")]
    cola = ama_service.cola_publicacion_resumen()
    return {
        "agentes": meta,
        "ultimo_ciclo": ultimo,
        "leads_total": len(leads),
        "reservas_activas": len(activas),
        "cola_pendientes": cola["pendientes"],
        "cola_aprobados": cola["aprobados"],
        "mensaje": "Pipeline de hoy o ciclo diario de 8 agentes.",
    }


def ejecutar_agente(
    db: Session,
    agent_id: str,
    *,
    task_ids: list[str] | None = None,
) -> dict:
    return run_agent(agent_id, db, task_ids=task_ids).to_dict()


def ejecutar_ciclo(db: Session) -> dict:
    return run_daily_cycle(db)


def crear_lead(body: dict) -> dict:
    return store.add_lead(
        body["nombre"],
        body["telefono"],
        email=body.get("email"),
        origen=body.get("origen", "whatsapp"),
        notas=body.get("notas", ""),
    )


def mensajes_reserva(db: Session, reserva_id: str) -> list[dict]:
    r = reserva_service.obtener(db, reserva_id)
    if not r:
        return []
    from backend.services.config_service import get_config

    cfg = get_config(db, "complejo")
    valor = cfg.get("valor") if cfg and isinstance(cfg.get("valor"), dict) else {}
    return sugerir_para_reserva(r, valor)
