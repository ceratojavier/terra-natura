"""
Agente CONTENIDO — redes sociales, calendario editorial, copy y video.
Integra el módulo AMA existente.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from agents.core.base import AgentRunResult, AgentStatus, AgentTask, BaseAgent, TaskResult
from backend.services import ama_service


class ContentSocialAgent(BaseAgent):
    agent_id = "content"
    nombre = "Contenido & Redes"
    descripcion = (
        "Calendario editorial, copy Instagram/Facebook/WhatsApp, "
        "campañas por eventos y coherencia con ocupación."
    )
    icono = "📱"

    def tareas_disponibles(self) -> list[AgentTask]:
        return [
            AgentTask("revisar_calendario", "Revisar publicaciones pendientes de aprobación"),
            AgentTask("sugerir_semana", "Sugerir plan de contenido 7 días"),
            AgentTask("alertas_eventos", "Alertar feriados / temporada (AMA)"),
            AgentTask("coherencia_stock", "Pausar piezas si unidad vendida (manual MVP)"),
            AgentTask("grilla_turismo", "Revisar grilla anual turismo (eventos Punilla)"),
        ]

    def ejecutar(
        self,
        db: Any | None = None,
        *,
        task_ids: list[str] | None = None,
    ) -> AgentRunResult:
        del db
        run = self._result_shell(AgentStatus.RUNNING)
        ids = task_ids or [t.id for t in self.tareas_disponibles()]

        if "revisar_calendario" in ids:
            dash = ama_service.dashboard()
            pend = dash.get("pendientes_aprobacion", 0)
            ok = pend < 8
            run.tareas.append(
                TaskResult(
                    "revisar_calendario",
                    ok,
                    f"{pend} publicación(es) esperan aprobación en /marketing",
                    {"dashboard": dash},
                )
            )
            if pend > 0:
                run.alertas.append(f"Aprobá {pend} post(s) en el panel de marketing")

        if "sugerir_semana" in ids:
            desde = date.today()
            sug = ama_service.generar_semana_api(desde, 7, guardar=False)
            items = sug.get("items", [])
            run.tareas.append(
                TaskResult(
                    "sugerir_semana",
                    True,
                    f"{len(items)} ideas listas para calendario",
                    {"muestra": items[:3]},
                )
            )

        if "alertas_eventos" in ids:
            from ama.engine.season_planner import alertas_proximas

            alerts = alertas_proximas(60)
            run.tareas.append(
                TaskResult(
                    "alertas_eventos",
                    True,
                    f"{len(alerts)} alerta(s) de temporada/feriado",
                    {"alertas": alerts[:5]},
                )
            )
            for a in alerts[:3]:
                run.alertas.append(a.get("mensaje", str(a)))

        if "coherencia_stock" in ids:
            run.tareas.append(
                TaskResult(
                    "coherencia_stock",
                    True,
                    "Revisá calendario si una unidad se vendió en OTA (pausar creativos)",
                    {"accion": "Panel marketing → borrador/pausado por unidad"},
                )
            )

        if "grilla_turismo" in ids:
            if db is not None:
                from backend.services import turismo_service

                g = turismo_service.grilla_anual(db)
                top = sorted(
                    [m for m in g["meses"] if m["total"] > 0],
                    key=lambda x: -x["total"],
                )[:3]
                run.tareas.append(
                    TaskResult(
                        "grilla_turismo",
                        True,
                        f"Grilla {g['anio']}: {g['resumen']['eventos']} eventos · ver /turismo",
                        {"meses_top": top, "export": f"agents/data/turismo/grilla_anual_{g['anio']}.json"},
                    )
                )
            else:
                run.tareas.append(
                    TaskResult("grilla_turismo", False, "Sin DB", {}),
                )

        run.status = (
            AgentStatus.WARNING if run.alertas else AgentStatus.OK
        )
        run.finalizado = self._now()
        return run
