"""
Video emotivo Kempes + hinchada REAL de Belgrano (Wikimedia CC) + cierre Bialet/Terra Natura.
NO usa imágenes inventadas de hinchadas.

python -m ama.video.fetch_belgrano_assets
python -m ama.video.cinematic_kempes belgrano
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

REPO = Path(__file__).resolve().parent.parent.parent
FOTOS = REPO / "archivos multimedia" / "fotos terra natura"
ASSETS = Path(__file__).resolve().parent.parent / "output" / "assets"
OUT = Path(__file__).resolve().parent.parent / "output" / "videos"

W, H = 720, 1280
FPS = 30


def _font(sz: int):
    for n in ("arialbd.ttf", "arial.ttf", "segoeuib.ttf"):
        try:
            return ImageFont.truetype(n, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def _load_cover(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    scale = max(W / im.width, H / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x, y = (nw - W) // 2, (nh - H) // 2
    return im.crop((x, y, x + W, y + H))


def _darken(im: Image.Image, factor: float = 0.62) -> Image.Image:
    return ImageEnhance.Brightness(im).enhance(factor)


def _vignette(im: Image.Image) -> Image.Image:
    overlay = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(50):
        draw.rectangle([(0, i), (W, i + 1)], fill=(0, 0, 0))
        draw.rectangle([(0, H - i - 1), (W, H - i)], fill=(0, 0, 0))
    return Image.blend(im, overlay, 0.32)


def _draw_text(im: Image.Image, lines: list[str], y0: int, size: int) -> Image.Image:
    draw = ImageDraw.Draw(im)
    font = _font(size)
    y = y0
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font, stroke_width=3)
        tw = bb[2] - bb[0]
        draw.text(
            ((W - tw) // 2, y),
            line,
            fill=(255, 255, 255),
            font=font,
            stroke_width=3,
            stroke_fill=(0, 0, 0),
        )
        y += (bb[3] - bb[1]) + 12
    return im


def _ken_burns(base: Image.Image, frames: int, zoom_in: bool) -> list[Image.Image]:
    out = []
    for i in range(frames):
        t = i / max(frames - 1, 1)
        scale = 1.0 + (0.22 * t if zoom_in else 0.22 * (1 - t))
        nw, nh = int(W * scale), int(H * scale)
        frame = base.resize((nw, nh), Image.Resampling.LANCZOS)
        x, y = (nw - W) // 2, (nh - H) // 2
        out.append(frame.crop((x, y, x + W, y + H)))
    return out


def _scene(path: Path, lines: list[str], seconds: float, zoom_in: bool) -> list[Image.Image]:
    n = max(1, int(seconds * FPS))
    base = _vignette(_darken(_load_cover(path)))
    if lines:
        base = _draw_text(base, lines, 100, 48 if len(lines) <= 2 else 40)
    return _ken_burns(base, n, zoom_in)


def _text_card(lines: list[str], seconds: float, bg=(8, 18, 14)) -> list[Image.Image]:
    n = max(1, int(seconds * FPS))
    return [
        _draw_text(Image.new("RGB", (W, H), bg), lines, H // 2 - 70, 54)
        for _ in range(n)
    ]


def _resolve_local(rel: str) -> Path | None:
    p = FOTOS / rel
    return p if p.is_file() else None


def _require_assets() -> None:
    required = (
        "kempes_aereo.jpg",
        "kempes_post_partido.jpg",
        "la14_presente.jpg",
        "belgrano_bandera.png",
    )
    missing = [n for n in required if not (ASSETS / n).is_file()]
    if missing:
        from ama.video.fetch_belgrano_assets import main as fetch

        fetch()
    still = [n for n in missing if not (ASSETS / n).is_file()]
    if still:
        raise SystemExit(f"Faltan assets: {still}. Ejecutá: python -m ama.video.fetch_belgrano_assets")


def build_belgrano() -> Path:
    _require_assets()

    frames: list[Image.Image] = []
    # Narrativa: Kempes → entrada → público real → LA 14 (hinchada Belgrano) → emoción → tu cabaña

    frames += _scene(ASSETS / "kempes_aereo.jpg", ["ESTE FINDE", "CÓRDOBA ES FÚTBOL"], 2.8, True)
    if (ASSETS / "kempes_ingreso.jpg").is_file():
        frames += _scene(ASSETS / "kempes_ingreso.jpg", ["RUMBO AL KEMPES"], 2.4, True)
    frames += _scene(
        ASSETS / "kempes_post_partido.jpg",
        ["LA GENTE LO SIENTE", "EN LA CANCHA"],
        3.2,
        False,
    )
    frames += _scene(
        ASSETS / "la14_presente.jpg",
        ["LA 14", "HINCHADA DE BELGRANO"],
        3.5,
        True,
    )
    if (ASSETS / "la14_fiesta.jpg").is_file():
        frames += _scene(ASSETS / "la14_fiesta.jpg", [], 2.2, False)
    frames += _text_card(["¿Y SI BELGRANO", "ES CAMPEÓN", "POR PRIMERA VEZ?"], 2.6)
    frames += _scene(ASSETS / "belgrano_bandera.png", ["FINAL EN EL KEMPES"], 2.2, False)
    if (ASSETS / "belgrano_partido.jpg").is_file():
        frames += _scene(ASSETS / "belgrano_partido.jpg", ["CELESTE Y BLANCO"], 2.0, True)

    frames += _text_card(["DESPUÉS DEL GRITO", "TU LUGAR EN BIALET MASSÉ"], 2.0)

    for rel, txt in (
        (
            "PARQUE/VISTA PANORAMICA DESDE EL COMPLEJO A TODO EL VALLE DE PUNILLA.jpg",
            ["CABAÑAS ALPINAS TERRA NATURA", "Los Talas 759 · Bialet Massé"],
        ),
        (
            "RIO Y BALNEARIOS/TOMANDO UNOS MATES EN LOS LABIOS DEL INDIO EN BIALET MASSE.jpg",
            ["A MINUTOS DEL LAGO Y EL RÍO"],
        ),
        ("PISCINA/PARQUE Y PISCINA.jpg", ["RESERVÁ TU FINDE", "WhatsApp 3541 571190"]),
    ):
        p = _resolve_local(rel)
        if p:
            frames += _scene(p, txt, 3.2, True)

    return _encode(frames, "kempes_belgrano_REAL_whatsapp.mp4")


def _encode(frames: list[Image.Image], filename: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / filename
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, fr in enumerate(frames):
            fr.save(tmp_path / f"f_{i:06d}.jpg", quality=92)
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise SystemExit("Instalá ffmpeg (winget install ffmpeg).")
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(tmp_path / "f_%06d.jpg"),
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
    print(dest)
    return dest


if __name__ == "__main__":
    build_belgrano()
