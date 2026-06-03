"""API — Video Pro Creator."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/video-pro", tags=["Video Pro Creator"])

_REPO = Path(__file__).resolve().parent.parent.parent
_UPLOAD = _REPO / "video_pro" / "uploads"
_OUTPUT = _REPO / "video_pro" / "output"


class GenerarPromptIn(BaseModel):
    personajes: str = ""
    ambientacion: str = ""
    iluminacion: str = ""
    estilo: str = ""
    modo: str = "wizard"


@router.get("/estado")
def estado():
    from video_pro.veo_client import estado_veo

    return {
        "app": "Video Pro Creator",
        "idioma": "es-ES",
        "veo": estado_veo(),
    }


@router.post("/generar-prompt")
def generar_prompt(body: GenerarPromptIn):
    from video_pro.prompt_director import VideoProInputs, generar_completo

    inputs = VideoProInputs(
        personajes=body.personajes,
        ambientacion=body.ambientacion,
        iluminacion=body.iluminacion,
        estilo=body.estilo,
        modo="wizard" if body.modo != "imagen" else "imagen",
    )
    return generar_completo(inputs)


@router.post("/imagen-a-video")
async def imagen_a_video(
    imagen: UploadFile = File(...),
    prompt: str = Form("", description="Qué debe pasar en el vídeo"),
    personajes: str = Form(""),
    ambientacion: str = Form(""),
    iluminacion: str = Form(""),
    estilo: str = Form("cinematográfico premium"),
    generar_veo: bool = Form(True),
):
    """Sube imagen, enriquece prompt y opcionalmente genera con Veo."""
    _UPLOAD.mkdir(parents=True, exist_ok=True)
    ext = Path(imagen.filename or "foto.jpg").suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    dest = _UPLOAD / f"{uuid.uuid4().hex}{ext}"
    with dest.open("wb") as f:
        shutil.copyfileobj(imagen.file, f)

    from video_pro.prompt_director import VideoProInputs, generar_completo
    from video_pro.veo_client import generar_video_desde_imagen

    inputs = VideoProInputs(
        personajes=personajes or "según la imagen",
        ambientacion=ambientacion or "según la imagen",
        iluminacion=iluminacion or "coherente con la foto",
        estilo=estilo,
        prompt_imagen=prompt,
        modo="imagen",
    )
    paquete = generar_completo(inputs)

    veo_result = None
    if generar_veo:
        veo_result = generar_video_desde_imagen(dest, paquete["prompt_final"])

    return {
        "ok": True,
        "imagen_subida": dest.name,
        "paquete": paquete,
        "veo": veo_result,
    }


@router.get("/archivo")
def descargar_archivo(ruta: str = Query(...)):
    if ".." in ruta or ruta.startswith("/"):
        raise HTTPException(400, "Ruta inválida")
    path = _REPO / ruta.replace("\\", "/")
    if not path.is_file() or "video_pro/output" not in str(path).replace("\\", "/"):
        raise HTTPException(404, "Archivo no encontrado")
    return FileResponse(path, media_type="video/mp4", filename=path.name)
