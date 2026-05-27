"""
Base para agentes Terra Natura — cada agente tiene id, rol y tareas auditables.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class AgentTask:
    id: str
    titulo: str
    descripcion: str = ""
    automatico: bool = True


@dataclass
class TaskResult:
    task_id: str
    ok: bool
    mensaje: str
    datos: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRunResult:
    agent_id: str
    nombre: str
    status: AgentStatus
    iniciado: str
    finalizado: str
    tareas: list[TaskResult] = field(default_factory=list)
    alertas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "nombre": self.nombre,
            "status": self.status.value,
            "iniciado": self.iniciado,
            "finalizado": self.finalizado,
            "tareas": [
                {
                    "task_id": t.task_id,
                    "ok": t.ok,
                    "mensaje": t.mensaje,
                    "datos": t.datos,
                }
                for t in self.tareas
            ],
            "alertas": self.alertas,
        }


class BaseAgent(ABC):
    agent_id: str
    nombre: str
    descripcion: str
    icono: str = "🤖"

    @abstractmethod
    def tareas_disponibles(self) -> list[AgentTask]:
        ...

    @abstractmethod
    def ejecutar(
        self,
        db: Any | None = None,
        *,
        task_ids: list[str] | None = None,
    ) -> AgentRunResult:
        ...

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _result_shell(self, status: AgentStatus = AgentStatus.RUNNING) -> AgentRunResult:
        t = self._now()
        return AgentRunResult(
            agent_id=self.agent_id,
            nombre=self.nombre,
            status=status,
            iniciado=t,
            finalizado=t,
        )
