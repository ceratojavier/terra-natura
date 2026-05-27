"""
Agente CALENDARIO — plan editorial 90 días, feriados, guiones y medios.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from agents.core.base import AgentRunResult, AgentStatus, AgentTask, BaseAgent, TaskResult


class CalendarEditorialAgent(BaseAgent):
    agent_id = "calendar"
    nombre = "Calendario editorial por rango"
    descripcion = (
        "Planifica publicaciones IG, Facebook, WhatsApp Status y TikTok. "
        "Feriados, puentes, vacaciones invierno, guiones, fotos y clips YouTube."
    )
    icono = "📅"

    def tareas_disponibles(self) -> list[AgentTask]:
        return [
            AgentTask(
                "planificar_90_dias",
                "Generar calendario 90 días (CTA + fidelización + utilidad)",
                automatico=False,
            ),
            AgentTask("alertas_feriados_puentes", "Alertas campaña 60/30/14/7 días antes de puentes"),
            AgentTask("resumen_calendario", "Resumen publicaciones en calendario AMA"),
            AgentTask("exportar_preview", "Export JSON último plan 90 días"),
            AgentTask(
                "generar_videos_editoriales",
                "Crear videos profesionales (fotos propias) para próximos reels",
                automatico=False,
            ),
        ]

    def ejecutar(
        self,
        db: Any | None = None,
        *,
        task_ids: list[str] | None = None,
    ) -> AgentRunResult:
        run = self._result_shell(AgentStatus.RUNNING)
        ids = task_ids or [t.id for t in self.tareas_disponibles()]

        if "planificar_90_dias" in ids:
            from backend.services.ama_service import generar_calendario_90_api

            r = generar_calendario_90_api(
                date.today(),
                90,
                guardar=True,
                reemplazar_borradores=False,
                db=db,
            )
            res = r.get("resumen", {})
            run.tareas.append(
                TaskResult(
                    "planificar_90_dias",
                    True,
                    f"Plan 90 días: {res.get('total', 0)} piezas · guardadas {r.get('guardadas', 0)}",
                    {"resumen": res, "export": r.get("export_json")},
                )
            )
            run.alertas.append("Revisá borradores en /marketing → Calendario")

        if "alertas_feriados_puentes" in ids:
            from ama.engine.calendar_context import alertas_campana_proximas

            alerts = alertas_campana_proximas(dias=90)
            run.tareas.append(
                TaskResult(
                    "alertas_feriados_puentes",
                    True,
                    f"{len(alerts)} recordatorio(s) de campaña por feriados/puentes",
                    {"alertas": alerts[:8]},
                )
            )
            for a in alerts[:3]:
                run.alertas.append(a.get("mensaje", ""))

        if "resumen_calendario" in ids:
            from ama.storage.calendar_store import list_publicaciones

            pubs = list_publicaciones()
            borrador = [p for p in pubs if p.get("estado") == "borrador"]
            run.tareas.append(
                TaskResult(
                    "resumen_calendario",
                    True,
                    f"{len(pubs)} en calendario · {len(borrador)} borrador(es)",
                    {"total": len(pubs), "borradores": len(borrador)},
                )
            )

        if "generar_videos_editoriales" in ids:
            from ama.video.editorial_reel_builder import build_lote_calendario

            r = build_lote_calendario(dias=14, max_videos=5, db=db)
            run.tareas.append(
                TaskResult(
                    "generar_videos_editoriales",
                    r.get("generados", 0) > 0,
                    f"{r.get('generados', 0)} video(s) editorial(es) generados",
                    r,
                )
            )
            if r.get("errores"):
                run.alertas.append(f"Videos con error: {len(r['errores'])}")

        if "exportar_preview" in ids:
            from pathlib import Path

            p = Path(__file__).resolve().parents[2] / "ama" / "data" / "calendario_90_ultimo.json"
            ok = p.is_file()
            run.tareas.append(
                TaskResult(
                    "exportar_preview",
                    ok,
                    f"Export: {p.name}" if ok else "Generá planificar_90_dias primero",
                    {"ruta": str(p) if ok else None},
                )
            )

        run.status = AgentStatus.WARNING if run.alertas else AgentStatus.OK
        run.finalizado = self._now()
        return run
