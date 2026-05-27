"""API — Configurador paso a paso (instalador Terra Natura)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services import setup_wizard_service as sw

router = APIRouter(prefix="/api/setup", tags=["Configurador"])


class PasoGuardarBody(BaseModel):
    valores: dict = Field(default_factory=dict)
    marcar_completo: bool = True


@router.get("/estado")
def estado():
    return sw.estado_completo()


@router.get("/pasos")
def listar_pasos():
    return {"pasos": sw.list_steps()}


@router.get("/paso/{step_id}")
def obtener_paso(step_id: str):
    try:
        return sw.obtener_paso(step_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


@router.put("/paso/{step_id}")
def guardar_paso(step_id: str, body: PasoGuardarBody):
    try:
        return sw.guardar_paso(step_id, body.valores, marcar_completo=body.marcar_completo)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


@router.post("/paso/{step_id}/adjunto")
async def subir_adjunto(step_id: str, archivo: UploadFile = File(...)):
    if not archivo.filename:
        raise HTTPException(400, "Archivo sin nombre")
    data = await archivo.read()
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(413, "Máximo 50 MB por archivo")
    return sw.guardar_adjunto(step_id, archivo.filename, data)


@router.get("/herramientas")
def herramientas():
    return sw.herramientas_detalle()


@router.get("/inflacion-proyeccion")
def inflacion_proyeccion():
    from backend.services.inflacion_proyeccion_service import obtener_proyeccion

    return obtener_proyeccion(refrescar_si_viejo=True)


@router.post("/inflacion-proyeccion/actualizar")
def inflacion_proyeccion_actualizar():
    from backend.services.inflacion_coeficiente_service import actualizar_serie_rem

    return actualizar_serie_rem(forzar=True)


@router.get("/coeficiente-inflacion")
def coeficiente_inflacion(fecha: str):
    """fecha=YYYY-MM-DD — coeficiente interanual mismo mes para esa noche."""
    from datetime import date as date_cls

    from backend.services.inflacion_coeficiente_service import coeficiente_interanual_mismo_mes

    try:
        f = date_cls.fromisoformat(fecha)
    except ValueError as e:
        raise HTTPException(400, "fecha inválida (use YYYY-MM-DD)") from e
    return coeficiente_interanual_mismo_mes(f)


@router.post("/sincronizar-agenda")
def sincronizar_agenda(db: Session = Depends(get_db)):
    from ama.scrapers.event_hunter import actualizar_agenda

    return actualizar_agenda(db=db, scrape_web=True)


@router.get("/snippet-env")
def snippet_env():
    """Fragmento .env sugerido (sin secretos del servidor)."""
    import json
    from pathlib import Path

    cfg_path = Path(__file__).resolve().parent.parent.parent / "local" / "config-dueño.json"
    lines = ["# Terra Natura — generado desde configurador"]
    if cfg_path.is_file():
        try:
            raw = json.loads(cfg_path.read_text(encoding="utf-8"))
            yt = (raw.get("datos", {}).get("youtube", {}) or {}).get("youtube_api_key")
            if yt:
                lines.append(f"YOUTUBE_API_KEY={yt}")
        except Exception:
            pass
    lines.append("WHATSAPP_VERIFY_TOKEN=")
    lines.append("DEBUG=true")
    return {"snippet": "\n".join(lines)}
