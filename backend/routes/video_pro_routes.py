"""API — Video Pro Creator + B-roll YouTube cinematográfico."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.config.database import get_db

router = APIRouter(prefix="/api/video-pro", tags=["Video Pro Creator"])

_REPO = Path(__file__).resolve().parent.parent.parent
_UPLOAD = _REPO / "video_pro" / "uploads"
_OUTPUT = _REPO / "video_pro" / "output"
_ALLOWED_DOWNLOAD_PREFIXES = (
    "video_pro/output/",
    "ama/output/videos/",
)


class GenerarPromptIn(BaseModel):
    personajes: str = ""
    ambientacion: str = ""
    iluminacion: str = ""
    estilo: str = ""
    modo: str = "wizard"


class BuscarYoutubeIn(BaseModel):
    termino: str = Field(..., min_length=2, description="Localidad o atracción")
    max_results: int = Field(8, ge=1, le=20)


class RecolectarYoutubeIn(BaseModel):
    nichos: list[str] | None = None
    max_por_nicho: int = Field(6, ge=1, le=15)
    guardar_bd: bool = True
    export_json: bool = True


class FusionarYoutubeIn(BaseModel):
    youtube_ids: list[str] = Field(..., min_length=1)
    duracion_por_clip: float = Field(5.0, ge=2.0, le=15.0)
    musica: bool = True
    titulo: str = "Reel B-roll Terra Natura"


class FusionarBusquedaIn(BaseModel):
    termino: str | None = None
    nicho_id: str | None = None
    max_clips: int = Field(4, ge=2, le=8)
    duracion_por_clip: float = Field(5.0, ge=2.0, le=15.0)
    musica: bool = True


class ReelProfesionalIn(BaseModel):
    prompt: str = Field(..., min_length=8)
    objetivo: str | None = None
    carpeta_fotos: str | None = None


def _get_youtube_api_key() -> str:
    import os
    from pathlib import Path

    from dotenv import load_dotenv

    root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(root / ".env", override=True)
    return os.getenv("YOUTUBE_API_KEY", "").strip()


def _youtube_key_ok() -> bool:
    key = _get_youtube_api_key()
    return bool(key and len(key) > 20)


@router.get("/estado")
def estado():
    from video_pro.video_generator import estado_generador

    gen = estado_generador()
    yt_ok = _youtube_key_ok()
    return {
        "app": "Video Pro Creator",
        "idioma": "es-ES",
        "generador": gen,
        "veo": gen.get("veo"),
        "huggingface": gen.get("huggingface"),
        "cuota": gen.get("cuota"),
        "disponible": gen.get("disponible"),
        "broll": {
            "youtube_api": yt_ok,
            "mensaje_youtube": (
                "Listo para buscar B-roll HD"
                if yt_ok
                else "Configurá YOUTUBE_API_KEY en .env — docs/YOUTUBE_API_SETUP.md"
            ),
            "ffmpeg": bool(shutil.which("ffmpeg")),
            "yt_dlp": bool(shutil.which("yt-dlp")),
        },
    }


@router.get("/youtube/nichos")
def youtube_nichos():
    from video_pro.youtube_cinematic import NICHOS

    return {"nichos": [{"id": n["id"], "nombre": n["nombre"], "localidad": n["localidad"]} for n in NICHOS]}


@router.post("/youtube/buscar")
def youtube_buscar(body: BuscarYoutubeIn):
    api_key = _get_youtube_api_key()
    if not (api_key and len(api_key) > 20):
        raise HTTPException(503, "Falta YOUTUBE_API_KEY en .env")
    from video_pro.youtube_cinematic import extraer_por_termino

    return extraer_por_termino(api_key, body.termino, max_results=body.max_results)


@router.post("/youtube/recolectar")
def youtube_recolectar(body: RecolectarYoutubeIn, db: Session = Depends(get_db)):
    from video_pro.youtube_cinematic import exportar_json_clips, recolectar_nichos

    api_key = _get_youtube_api_key()
    if not (api_key and len(api_key) > 20):
        raise HTTPException(503, "Falta YOUTUBE_API_KEY en .env")

    payload = recolectar_nichos(
        api_key,
        nicho_ids=body.nichos,
        max_por_nicho=body.max_por_nicho,
    )

    json_path = None
    if body.export_json and payload.get("videos"):
        json_path = exportar_json_clips(payload)

    bd_stats = None
    if body.guardar_bd:
        from backend.services.youtube_turismo import recolectar_videos

        bd_stats = recolectar_videos(db, max_por_query=body.max_por_nicho)

    return {
        **payload,
        "json_export": str(json_path.relative_to(_REPO).as_posix()) if json_path else None,
        "bd": bd_stats,
    }


@router.post("/youtube/fusionar")
def youtube_fusionar(body: FusionarYoutubeIn):
    from video_pro.reel_fusion import fusionar_clips_youtube

    result = fusionar_clips_youtube(
        body.youtube_ids,
        duracion_por_clip=body.duracion_por_clip,
        titulo=body.titulo,
        musica=body.musica,
    )
    if not result.get("ok"):
        raise HTTPException(400, result.get("error") or "Error al fusionar")
    return result


@router.post("/youtube/fusionar-busqueda")
def youtube_fusionar_busqueda(body: FusionarBusquedaIn):
    from video_pro.reel_fusion import fusionar_desde_busqueda

    api_key = _get_youtube_api_key()
    if not (api_key and len(api_key) > 20):
        raise HTTPException(503, "Falta YOUTUBE_API_KEY en .env")
    if not body.termino and not body.nicho_id:
        raise HTTPException(400, "Indicá termino o nicho_id")

    result = fusionar_desde_busqueda(
        api_key,
        termino=body.termino,
        nicho_id=body.nicho_id,
        max_clips=body.max_clips,
        duracion_por_clip=body.duracion_por_clip,
        musica=body.musica,
    )
    if not result.get("ok"):
        raise HTTPException(400, result.get("error") or "Error al fusionar")
    return result


@router.post("/reel-profesional")
def reel_profesional(body: ReelProfesionalIn, db: Session = Depends(get_db)):
    """
    Prompt + fotos galería + B-roll YouTube → reel cinematográfico alternado.
    Movimiento suave (ffmpeg), subtítulos ASS, música — no slideshow con zoom brusco.
    """
    from video_pro.pro_reel_producer import producir_reel_profesional

    result = producir_reel_profesional(
        body.prompt,
        objetivo=body.objetivo,
        db=db,
        carpeta_fotos=body.carpeta_fotos,
    )
    if not result.get("ok"):
        raise HTTPException(400, result.get("error") or result.get("mensaje") or "Error al generar")
    ruta = result.get("ruta") or result.get("ruta_visible")
    if ruta:
        result["url_descarga"] = f"/api/video-pro/archivo?ruta={ruta}"
    return result


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
    generar_video: bool = Form(True, alias="generar_veo"),
):
    """Sube imagen, enriquece prompt y opcionalmente genera vídeo (HF gratis por defecto)."""
    _UPLOAD.mkdir(parents=True, exist_ok=True)
    ext = Path(imagen.filename or "foto.jpg").suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    dest = _UPLOAD / f"{uuid.uuid4().hex}{ext}"
    with dest.open("wb") as f:
        shutil.copyfileobj(imagen.file, f)

    from video_pro.prompt_director import VideoProInputs, generar_completo
    from video_pro.video_generator import generar_video_desde_imagen

    inputs = VideoProInputs(
        personajes=personajes or "según la imagen",
        ambientacion=ambientacion or "según la imagen",
        iluminacion=iluminacion or "coherente con la foto",
        estilo=estilo,
        prompt_imagen=prompt,
        modo="imagen",
    )
    paquete = generar_completo(inputs)

    video_result = None
    if generar_video:
        video_result = generar_video_desde_imagen(dest, paquete["prompt_final"])

    return {
        "ok": True,
        "imagen_id": dest.name,
        "imagen_subida": dest.name,
        "paquete": paquete,
        "video": video_result,
        "veo": video_result,
    }


@router.post("/generar-video")
async def generar_video_endpoint(
    imagen_id: str = Form(..., description="Nombre devuelto al subir la imagen"),
    prompt: str = Form("", description="Prompt final enriquecido"),
):
    """Genera el MP4 a partir de una imagen ya subida."""
    from video_pro.video_generator import generar_video_desde_imagen

    path = _UPLOAD / Path(imagen_id).name
    if not path.is_file() or path.parent.resolve() != _UPLOAD.resolve():
        raise HTTPException(404, "Imagen no encontrada. Volvé a subir la foto.")

    prompt = prompt.strip()
    if not prompt:
        raise HTTPException(400, "Falta el prompt. Volvé al paso anterior.")

    video_result = generar_video_desde_imagen(path, prompt, prompt_ya_listo=True)
    ok = bool(video_result.get("ok"))
    return {
        "ok": ok,
        "video": video_result,
        "veo": video_result,
        "imagen_id": path.name,
    }


@router.get("/archivo")
def descargar_archivo(ruta: str = Query(...)):
    if ".." in ruta or ruta.startswith("/"):
        raise HTTPException(400, "Ruta inválida")
    norm = ruta.replace("\\", "/")
    if not any(norm.startswith(p) for p in _ALLOWED_DOWNLOAD_PREFIXES):
        raise HTTPException(400, "Ruta no permitida")
    path = _REPO / norm
    if not path.is_file():
        raise HTTPException(404, "Archivo no encontrado")
    return FileResponse(path, media_type="video/mp4", filename=path.name)
