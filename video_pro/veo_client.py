"""
Google Veo 3.x — generación de vídeo desde imagen + prompt (requiere GOOGLE_AI_API_KEY o GEMINI_API_KEY).
"""
from __future__ import annotations

import base64
import os
import time
import uuid
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent
_OUTPUT = _REPO / "video_pro" / "output"


def _api_key() -> str | None:
    return os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")


def estado_veo() -> dict[str, Any]:
    key = _api_key()
    return {
        "disponible": bool(key),
        "modelo": os.getenv("VEO_MODEL", "veo-3.1-generate-preview"),
        "mensaje": (
            "Veo conectado: podés generar vídeo desde imagen."
            if key
            else "Añadí GOOGLE_AI_API_KEY o GEMINI_API_KEY en .env para generar con Veo."
        ),
        "docs": "https://ai.google.dev/gemini-api/docs/video",
    }


def generar_video_desde_imagen(
    imagen: Path,
    prompt: str,
    *,
    duracion_seg: float = 5.0,
) -> dict[str, Any]:
    """
    Intenta generar vídeo con API Gemini/Veo.
    Si falla, devuelve prompt enriquecido para uso manual.
    """
    from video_pro.prompt_director import VideoProInputs, generar_completo

    key = _api_key()
    _OUTPUT.mkdir(parents=True, exist_ok=True)
    out_id = uuid.uuid4().hex[:12]
    out_path = _OUTPUT / f"veo_{out_id}.mp4"

    inputs = VideoProInputs(
        personajes="según imagen de referencia",
        ambientacion="coherente con la fotografía",
        iluminacion="coherente con la imagen",
        estilo="cinematográfico premium",
        prompt_imagen=prompt,
        modo="imagen",
    )
    paquete = generar_completo(inputs)
    prompt_enriquecido = paquete["prompt_final"]

    if not key:
        return {
            "ok": False,
            "error": "veo_sin_api_key",
            "mensaje_usuario": "Sin clave de Google AI. Copiá el prompt y usadlo en Google AI Studio.",
            "prompt_enriquecido": prompt_enriquecido,
            "paquete": paquete,
            "manual_url": "https://aistudio.google.com/",
        }

    if not imagen.is_file():
        return {"ok": False, "error": "imagen_no_encontrada", "mensaje_usuario": "No se encontró la imagen."}

    try:
        return _generar_con_sdk(imagen, prompt_enriquecido, out_path, duracion_seg)
    except ImportError:
        return _generar_con_http(imagen, prompt_enriquecido, out_path, key)
    except Exception as e:
        return {
            "ok": False,
            "error": "veo_error",
            "mensaje_usuario": f"No se pudo generar con Veo: {e}. Usá el prompt copiado en AI Studio.",
            "prompt_enriquecido": prompt_enriquecido,
            "paquete": paquete,
            "manual_url": "https://aistudio.google.com/",
        }


def _generar_con_sdk(imagen: Path, prompt: str, out_path: Path, duracion_seg: float) -> dict[str, Any]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_api_key())
    model = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")

    image_bytes = imagen.read_bytes()
    mime = "image/jpeg" if imagen.suffix.lower() in (".jpg", ".jpeg") else "image/png"

    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        image=types.Image(image_bytes=image_bytes, mime_type=mime),
        config=types.GenerateVideosConfig(
            number_of_videos=1,
            duration_seconds=int(min(8, max(4, duracion_seg))),
        ),
    )

    deadline = time.time() + 300
    while not operation.done:
        if time.time() > deadline:
            return {
                "ok": False,
                "error": "veo_timeout",
                "mensaje_usuario": "Veo tardó demasiado. Reintentá o usá el prompt en AI Studio.",
                "prompt_enriquecido": prompt,
            }
        time.sleep(8)
        operation = client.operations.get(operation)

    result = operation.result
    if not result or not result.generated_videos:
        return {
            "ok": False,
            "error": "veo_sin_resultado",
            "mensaje_usuario": "Veo no devolvió vídeo. Revisá cuota o modelo.",
            "prompt_enriquecido": prompt,
        }

    video = result.generated_videos[0]
    client.files.download(file=video.video, download_path=str(out_path))

    rel = out_path.relative_to(_REPO).as_posix()
    return {
        "ok": True,
        "mensaje_usuario": "Vídeo generado con Veo.",
        "ruta": rel,
        "url_descarga": f"/api/video-pro/archivo?ruta={rel}",
        "prompt_usado": prompt,
    }


def _generar_con_http(imagen: Path, prompt: str, out_path: Path, key: str) -> dict[str, Any]:
    """Fallback REST si no está instalado google-genai."""
    import httpx

    model = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")
    b64 = base64.standard_b64encode(imagen.read_bytes()).decode("ascii")
    mime = "image/jpeg" if imagen.suffix.lower() in (".jpg", ".jpeg") else "image/png"

    base = "https://generativelanguage.googleapis.com/v1beta"
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}

    body = {
        "instances": [
            {
                "prompt": prompt,
                "image": {"bytesBase64Encoded": b64, "mimeType": mime},
            }
        ],
        "parameters": {"sampleCount": 1},
    }

    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{base}/models/{model}:predictLongRunning", json=body, headers=headers)
        if r.status_code >= 400:
            return {
                "ok": False,
                "error": "veo_http",
                "mensaje_usuario": (
                    f"API Veo respondió {r.status_code}. Instalá: pip install google-genai "
                    "o generá en https://aistudio.google.com/"
                ),
                "prompt_enriquecido": prompt,
                "detalle": r.text[:500],
            }
        op_name = r.json().get("name")
        if not op_name:
            return {"ok": False, "error": "veo_sin_operacion", "prompt_enriquecido": prompt}

        deadline = time.time() + 300
        while time.time() < deadline:
            time.sleep(10)
            poll = client.get(f"{base}/{op_name}", headers=headers)
            data = poll.json()
            if data.get("done"):
                # Estructura puede variar; guardar referencia
                return {
                    "ok": False,
                    "error": "veo_descarga_manual",
                    "mensaje_usuario": (
                        "Operación Veo completada. Descargá el archivo desde Google AI Studio "
                        "o instalá google-genai para descarga automática."
                    ),
                    "prompt_enriquecido": prompt,
                    "operacion": data,
                    "manual_url": "https://aistudio.google.com/",
                }
    return {"ok": False, "error": "veo_timeout", "prompt_enriquecido": prompt}
