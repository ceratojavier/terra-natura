"""Registro de agentes del ecosistema Terra Natura."""
from __future__ import annotations

from agents.calendar.agent import CalendarEditorialAgent
from agents.channels.agent import ChannelManagerAgent
from agents.content.agent import ContentSocialAgent
from agents.crm.agent import CrmComunicacionAgent
from agents.core.base import BaseAgent

AGENT_REGISTRY: dict[str, BaseAgent] = {
    CalendarEditorialAgent.agent_id: CalendarEditorialAgent(),
    ContentSocialAgent.agent_id: ContentSocialAgent(),
    CrmComunicacionAgent.agent_id: CrmComunicacionAgent(),
    ChannelManagerAgent.agent_id: ChannelManagerAgent(),
}


def get_agent(agent_id: str) -> BaseAgent:
    if agent_id not in AGENT_REGISTRY:
        raise KeyError(f"Agente desconocido: {agent_id}")
    return AGENT_REGISTRY[agent_id]


def list_agents_meta() -> list[dict]:
    out = []
    for a in AGENT_REGISTRY.values():
        out.append(
            {
                "id": a.agent_id,
                "nombre": a.nombre,
                "descripcion": a.descripcion,
                "icono": a.icono,
                "tareas": [
                    {"id": t.id, "titulo": t.titulo, "automatico": t.automatico}
                    for t in a.tareas_disponibles()
                ],
            }
        )
    return out
