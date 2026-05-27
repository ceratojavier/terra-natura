from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.schemas.agents import AgentRunRequest, LeadCreate
from backend.services import agents_service

router = APIRouter(prefix="/api/agentes", tags=["Agentes Terra Natura"])


@router.get("/hub")
def hub(db: Session = Depends(get_db)):
    return agents_service.hub_dashboard(db)


@router.get("")
def listar_agentes():
    from agents.core.registry import list_agents_meta

    return {"agentes": list_agents_meta()}


@router.post("/ciclo-diario")
def ciclo_diario(db: Session = Depends(get_db)):
    return agents_service.ejecutar_ciclo(db)


@router.post("/{agent_id}/ejecutar")
def ejecutar_agente(
    agent_id: str,
    body: AgentRunRequest | None = None,
    db: Session = Depends(get_db),
):
    try:
        return agents_service.ejecutar_agente(
            db,
            agent_id,
            task_ids=body.task_ids if body else None,
        )
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@router.get("/crm/leads")
def crm_leads(estado: str | None = None):
    from agents.crm import store

    return {"leads": store.list_leads(estado)}


@router.post("/crm/leads")
def crm_crear_lead(body: LeadCreate):
    from agents.crm import store

    return store.add_lead(
        body.nombre,
        body.telefono,
        email=body.email,
        origen=body.origen,
        notas=body.notas,
    )


@router.get("/crm/reservas/{reserva_id}/mensajes")
def crm_mensajes_reserva(reserva_id: str, db: Session = Depends(get_db)):
    msgs = agents_service.mensajes_reserva(db, reserva_id)
    from backend.services import reserva_service

    if not msgs and reserva_service.obtener(db, reserva_id) is None:
        raise HTTPException(404, "Reserva no encontrada")
    return {"mensajes": msgs}
