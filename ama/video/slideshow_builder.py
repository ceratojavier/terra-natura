"""
Slideshow MP4 con fotos locales + texto (MoviePy opcional).
Salida: ama/output/videos/
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_MEDIA = _REPO / "archivos multimedia"
_OUT = Path(__file__).resolve().parent.parent / "output" / "videos"


def _buscar_fotos(carpeta_rel: str | None, max_fotos: int = 8) -> list[Path]:
    base = _MEDIA
    if carpeta_rel:
        base = _MEDIA / carpeta_rel.replace("\\", "/").strip("/")
    if not base.is_dir():
        base = _MEDIA
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    fotos: list[Path] = []
    for p in sorted(base.rglob("*")):
        if p.suffix.lower() in exts and p.is_file():
            fotos.append(p)
            if len(fotos) >= max_fotos:
                break
    return fotos


def crear_slideshow(
    *,
    titulo_en_video: str = "Terra Natura · Bialet Massé",
    subtitulo: str = "Consultá por WhatsApp",
    carpeta_media: str | None = None,
    duracion_por_foto: float = 3.0,
) -> dict:
    """
    Devuelve {ok, ruta, mensaje, brief_canva}.
    Si MoviePy no está instalado, devuelve brief para armar en Canva gratis.
    """
    fotos = _buscar_fotos(carpeta_media)
    brief = (
        f"Video manual Canva: 5–8 fotos de {carpeta_media or 'parque/alpinas'}, "
        f"título «{titulo_en_video}», cierre «{subtitulo}», música libre de derechos."
    )

    if not fotos:
        return {
            "ok": False,
            "ruta": None,
            "mensaje": "No encontré fotos en archivos multimedia/. Agregá imágenes o indicá carpeta.",
            "brief_canva": brief,
        }

    try:
        from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
    except ImportError:
        return {
            "ok": False,
            "ruta": None,
            "mensaje": "MoviePy no instalado. En la PC del servidor: pip install moviepy. Mientras tanto usá el brief Canva.",
            "brief_canva": brief,
            "fotos_encontradas": [str(p.relative_to(_REPO)) for p in fotos[:5]],
        }

    _OUT.mkdir(parents=True, exist_ok=True)
    clips = []
    size = (1080, 1080)
    for foto in fotos:
        clip = ImageClip(str(foto)).resize(height=1080).crop(x_center=540, width=1080, height=1080)
        clip = clip.set_duration(duracion_por_foto)
        clips.append(clip)

    if not clips:
        return {"ok": False, "ruta": None, "mensaje": "Sin clips", "brief_canva": brief}

    video = concatenate_videoclips(clips, method="compose")
    try:
        txt = TextClip(
            titulo_en_video,
            fontsize=48,
            color="white",
            font="Arial",
            stroke_color="black",
            stroke_width=2,
        )
        txt = txt.set_position(("center", 80)).set_duration(video.duration)
        video = CompositeVideoClip([video, txt])
    except Exception:
        pass

    nombre = f"terra_natura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    destino = _OUT / nombre
    video.write_videofile(
        str(destino),
        fps=24,
        codec="libx264",
        audio=False,
        logger=None,
    )
    video.close()

    return {
        "ok": True,
        "ruta": str(destino.relative_to(_REPO)).replace("\\", "/"),
        "mensaje": "Video generado en carpeta ama/output/videos/",
        "brief_canva": brief,
        "fotos_usadas": len(fotos),
    }
