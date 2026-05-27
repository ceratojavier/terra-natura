from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    task_ids: list[str] | None = Field(
        default=None,
        description="Si vacío, ejecuta todas las tareas del agente",
    )


class LeadCreate(BaseModel):
    nombre: str
    telefono: str
    email: str | None = None
    origen: str = "whatsapp"
    notas: str = ""
