"""
Frames de marca Terra Natura — vertical 1080×1920, tipografía y gradientes.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

W, H = 1080, 1920
FPS = 30

# Paleta marca (verde bosque + dorado suave)
BG_DARK = (12, 28, 22)
BG_CARD = (18, 42, 32)
ACCENT = (180, 145, 85)
TEXT_MAIN = (255, 252, 245)
TEXT_SUB = (200, 220, 210)


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _font(size: int, bold: bool = True):
    names = ("arialbd.ttf", "segoeuib.ttf", "arial.ttf") if bold else ("arial.ttf", "segoeuib.ttf")
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _gradient_bottom(im: Image.Image, height: int = 420, alpha: float = 0.72) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(height):
        a = int(255 * alpha * (i / height))
        draw.rectangle([(0, H - height + i), (W, H - height + i + 1)], fill=(8, 20, 14, a))
    base = im.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def _draw_lines_center(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    y_start: int,
    font_main,
    font_sub=None,
    sub_from: int = 1,
) -> int:
    y = y_start
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        font = font_main if i < sub_from else (font_sub or font_main)
        bb = draw.textbbox((0, 0), line, font=font, stroke_width=3)
        tw = bb[2] - bb[0]
        th = bb[3] - bb[1]
        draw.text(
            ((W - tw) // 2, y),
            line,
            fill=TEXT_MAIN if i < sub_from else TEXT_SUB,
            font=font,
            stroke_width=3,
            stroke_fill=(0, 0, 0),
        )
        y += th + 14
    return y


def hook_card(lines: list[str], seconds: float, fps: int = FPS) -> list[Image.Image]:
    """Apertura emocional — fondo marca + gancho."""
    n = max(2, int(seconds * fps))
    frames: list[Image.Image] = []
    f_main = _font(62)
    f_sub = _font(40, bold=False)
    for i in range(n):
        t = _ease(i / max(1, n - 1))
        im = Image.new("RGB", (W, H), BG_CARD)
        draw = ImageDraw.Draw(im)
        # línea decorativa
        lw = int(W * 0.35 * t)
        draw.rectangle([(W - lw) // 2, 280, (W + lw) // 2, 284], fill=ACCENT)
        _draw_lines_center(draw, lines[:3], 320 + int(20 * (1 - t)), f_main, f_sub, sub_from=1)
        draw.text((W // 2 - 120, H - 120), "TERRA NATURA", fill=ACCENT, font=_font(28))
        frames.append(im)
    return frames


def cta_card(lines: list[str], seconds: float, fps: int = FPS) -> list[Image.Image]:
    n = max(2, int(seconds * fps))
    frames: list[Image.Image] = []
    f1 = _font(56)
    f2 = _font(44, bold=False)
    for i in range(n):
        im = Image.new("RGB", (W, H), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw.ellipse([(W // 2 - 90, 200), (W // 2 + 90, 380)], outline=ACCENT, width=4)
        _draw_lines_center(draw, lines, 420, f1, f2, sub_from=1)
        draw.text((W // 2 - 200, H - 160), "WhatsApp · 3541 571190", fill=ACCENT, font=_font(32))
        frames.append(im)
    return frames


def _prepare_photo(im: Image.Image, margin: float = 1.5) -> Image.Image:
    im = im.convert("RGB")
    scale = max(W / im.width, H / im.height) * margin
    nw, nh = int(im.width * scale), int(im.height * scale)
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def photo_scene(
    path: Path,
    seconds: float,
    effect: str,
    lines: list[str] | None,
    fps: int = FPS,
    warmth: float = 1.08,
) -> list[Image.Image]:
    big = _prepare_photo(Image.open(path))
    max_x = max(0, big.width - W)
    max_y = max(0, big.height - H)
    n = max(2, int(seconds * fps))
    frames: list[Image.Image] = []
    f_line = _font(48)
    f_small = _font(34, bold=False)

    for i in range(n):
        t = _ease(i / max(1, n - 1))
        if effect == "zoom_in":
            z = 1.0 - 0.22 * t
            cw, ch = int(big.width * z), int(big.height * z)
            resized = big.resize((cw, ch), Image.Resampling.LANCZOS)
            left = (resized.width - W) // 2
            top = (resized.height - H) // 2
            frame = resized.crop((left, top, left + W, top + H))
        elif effect == "zoom_out":
            z = 0.78 + 0.22 * t
            cw, ch = int(big.width * z), int(big.height * z)
            resized = big.resize((cw, ch), Image.Resampling.LANCZOS)
            left = (resized.width - W) // 2
            top = (resized.height - H) // 2
            frame = resized.crop((left, top, left + W, top + H))
        elif effect == "drift_zoom":
            z = 1.0 - 0.15 * t
            resized = big.resize((int(big.width * z), int(big.height * z)), Image.Resampling.LANCZOS)
            mx, my = max(0, resized.width - W), max(0, resized.height - H)
            left = int(mx * 0.25 * t)
            top = int(my * 0.15 * (1 - t))
            frame = resized.crop((left, top, left + W, top + H))
        else:
            left = int(max_x * 0.3 * t)
            top = max_y // 4
            frame = big.crop((left, top, left + W, top + H))

        frame = ImageEnhance.Color(frame).enhance(warmth)
        frame = ImageEnhance.Contrast(frame).enhance(1.05)
        frame = _gradient_bottom(frame)
        if lines and i > n // 8:
            draw = ImageDraw.Draw(frame)
            _draw_lines_center(draw, lines, H - 280, f_line, f_small, sub_from=1)
        frames.append(frame)
    return frames


def crossfade(a: Image.Image, b: Image.Image, steps: int = 14) -> list[Image.Image]:
    return [Image.blend(a, b, (i + 1) / steps) for i in range(steps)]


def join_scenes(parts: list[list[Image.Image]], fade_frames: int = 12) -> list[Image.Image]:
    if not parts:
        return []
    out = list(parts[0])
    for nxt in parts[1:]:
        if fade_frames > 0 and out and nxt:
            blend = crossfade(out[-1], nxt[0], fade_frames)
            out = out[:-1] + blend + nxt[fade_frames:]
        else:
            out.extend(nxt)
    return out
