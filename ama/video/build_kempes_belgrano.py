"""
Video Kempes — hinchas BELGRANO / interior Córdoba · base en Bialet Massé (no Villa General Belgrano).
python -m ama.video.build_kempes_belgrano
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent.parent
FOTOS = REPO / "archivos multimedia" / "fotos terra natura"
OUT = Path(__file__).resolve().parent.parent / "output" / "videos"

W, H = 720, 1280
FPS = 24
BG = (15, 31, 24)

SLIDES: list[tuple[str, str, float]] = [
    ("", "FIN DE SEMANA HISTÓRICO\nEN CÓRDOBA", 2.8),
    ("", "FINAL EN EL KEMPES", 2.2),
    ("", "¿Y SI BELGRANO\nES CAMPEÓN\nPOR PRIMERA VEZ?", 3.0),
    (
        "RIO Y BALNEARIOS/RIO COSQUIN EN BIALET MASSE.jpg",
        "Vos estás en Bialet Massé",
        2.8,
    ),
    (
        "RIO Y BALNEARIOS/TOMANDO UNOS MATES EN LOS LABIOS DEL INDIO EN BIALET MASSE.jpg",
        "A minutos del arroyo y el lago",
        2.8,
    ),
    (
        "PARQUE/VISTA PANORAMICA DESDE EL COMPLEJO A TODO EL VALLE DE PUNILLA.jpg",
        "Valle de Punilla desde el complejo",
        2.8,
    ),
    (
        "exteriores cabanas/VISTA PANORAMICA DEL COMPLEJO.jpg",
        "Tu refugio después del partido",
        2.8,
    ),
    ("PISCINA/PARQUE Y PISCINA.jpg", "Pileta · parque · descanso", 2.5),
    ("", "CABAÑAS ALPINAS\nTERRA NATURA\nLos Talas 759 · Bialet Massé", 2.5),
    ("", "RESERVÁ TU FINDE\nWhatsApp 3541 571190", 3.5),
]


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("arialbd.ttf", "arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _resolve(rel: str) -> Path | None:
    if not rel:
        return None
    p = FOTOS / rel
    return p if p.is_file() else None


def _fit_image(im: Image.Image, box_w: int, box_h: int) -> Image.Image:
    im = im.convert("RGB")
    im.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (box_w, box_h), BG)
    x = (box_w - im.width) // 2
    y = (box_h - im.height) // 2
    canvas.paste(im, (x, y))
    return canvas


def _render_frame(texto: str, foto: Path | None) -> Image.Image:
    frame = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(frame)
    font_title = _font(40)
    font_small = _font(26)

    y_text = 48
    for line in texto.split("\n"):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y_text), line, fill=(242, 239, 232), font=font_title)
        y_text += (bbox[3] - bbox[1]) + 10

    if foto:
        try:
            im = Image.open(foto)
            photo = _fit_image(im, W - 80, H - y_text - 110)
            frame.paste(photo, (40, y_text + 16))
        except OSError:
            pass

    draw.rectangle([(0, H - 8), (W, H)], fill=(45, 110, 75))
    marca = "Bialet Massé · Terra Natura"
    bb = draw.textbbox((0, 0), marca, font=font_small)
    draw.text(((W - (bb[2] - bb[0])) // 2, H - 52), marca, fill=(201, 169, 98), font=font_small)
    return frame


def build() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "kempes_belgrano_finde_whatsapp.mp4"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        idx = 0
        for rel, texto, dur in SLIDES:
            img = _render_frame(texto, _resolve(rel))
            n_frames = max(1, int(dur * FPS))
            for _ in range(n_frames):
                img.save(tmp_path / f"frame_{idx:05d}.jpg", quality=88)
                idx += 1

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise SystemExit("Instalá ffmpeg.")

        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(tmp_path / "frame_%05d.jpg"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(dest),
            ],
            check=True,
            capture_output=True,
        )

    print(f"Video listo: {dest}")
    return dest


if __name__ == "__main__":
    build()
