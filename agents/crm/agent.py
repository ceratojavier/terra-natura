"""
Agente CRM — leads, flujo WhatsApp/email, mensajes pre/durante/post estadía.
"""
from __future__ import annotations

from typing import Any

from agents.core.base import AgentRunResult, AgentStatus, AgentTask, BaseAgent, TaskResult
from agents.crm import store
from agents.crm.templates import leads_desde_reservas_pendientes, sugerir_para_reserva


class CrmComunicacionAgent(BaseAgent):
    agent_id = "crm"
    nombre = "CRM & Comunicación"
    descripcion = (
        "Consultas, confirmaciones, recordatorios T-24h y post estadía. "
        "Centraliza leads y mensajes sugeridos (copiar a WhatsApp)."
    )
    icono = "💬"

    def tareas_disponibles(self) -> list[AgentTask]:
        return [
            AgentTask("inbox_pendientes", "Reservas y leads que requieren respuesta"),
            AgentTask("mensajes_automaticos", "Generar borradores según estado"),
            AgentTask("seguimiento_leads", "Leads en consulta sin cerrar"),
            AgentTask("post_estadia", "Cola de agradecimiento + reseña Google"),
        ]

    def ejecutar(
        self,
        db: Any | None = None,
        *,
        task_ids: list[str] | None = None,
    ) -> AgentRunResult:
        run = self._result_shell(AgentStatus.RUNNING)
        ids = task_ids or [t.id for t in self.tareas_disponibles()]

        reservas: list[dict] = []
        config: dict | None = None
        if db is not None:
            from backend.services.reserva_service import listar

            reservas = listar(db, None, None, None)
            from backend.services.config_service import get_config

            c = get_config(db, "complejo")
            if c:
                config = c.get("valor") if isinstance(c.get("valor"), dict) else {}

        if "inbox_pendientes" in ids:
            pend = leads_desde_reservas_pendientes(reservas)
            leads = store.list_leads("consulta")
            run.tareas.append(
                TaskResult(
                    "inbox_pendientes",
                    True,
                    f"{pend} reserva(s) con seguimiento · {len(leads)} lead(s) en consulta",
                    {"reservas_pendientes": pend, "leads_consulta": len(leads)},
                )
            )
            if pend or leads:
                run.alertas.append("Hay conversaciones pendientes en panel / CRM")

        if "mensajes_automaticos" in ids:
            muestras = []
            for r in reservas[:5]:
                msgs = sugerir_para_reserva(r, config)
                if msgs:
                    muestras.append(
                        {
                            "reserva_id": r.get("id"),
                            "huesped": r.get("huesped_nombre"),
                            "mensaje": msgs[0],
                        }
                    )
            run.tareas.append(
                TaskResult(
                    "mensajes_automaticos",
                    True,
                    f"{len(muestras)} borrador(es) listos para copiar",
                    {"muestras": muestras},
                )
            )

        if "seguimiento_leads" in ids:
            leads = store.list_leads()
            run.tareas.append(
                TaskResult(
                    "seguimiento_leads",
                    True,
                    f"{len(leads)} lead(s) registrados",
                    {"leads": leads[-5:]},
                )
            )

        if "post_estadia" in ids:
            post = [r for r in reservas if r.get("estado") == "cerrada"][-3:]
            run.tareas.append(
                TaskResult(
                    "post_estadia",
                    True,
                    f"{len(post)} última(s) cerrada(s) — revisar mensaje reseña",
                    {"reservas": post},
                )
            )

        run.status = AgentStatus.WARNING if run.alertas else AgentStatus.OK
        run.finalizado = self._now()
        return run
