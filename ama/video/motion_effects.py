"""Efectos de movimiento (Ken Burns, paneo, fundidos) para fotos fijas."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

W, H = 720, 1280


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _font(sz: int):
    for n in ("arialbd.ttf", "arial.ttf", "segoeuib.ttf"):
        try:
            return ImageFont.truetype(n, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def _prepare_source(im: Image.Image, margin: float = 1.45) -> Image.Image:
    im = im.convert("RGB")
    scale = max(W / im.width, H / im.height) * margin
    nw, nh = int(im.width * scale), int(im.height * scale)
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def _crop_window(big: Image.Image, left: int, top: int) -> Image.Image:
    return big.crop((left, top, left + W, top + H))


def _vignette(im: Image.Image, strength: float = 0.28) -> Image.Image:
    overlay = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(45):
        draw.rectangle([(0, i), (W, i + 1)], fill=(0, 0, 0))
        draw.rectangle([(0, H - i - 1), (W, H - i)], fill=(0, 0, 0))
    return Image.blend(im, overlay, strength)


def _overlay_text(im: Image.Image, lines: list[str], size: int = 46) -> Image.Image:
    if not lines:
        return im
    draw = ImageDraw.Draw(im)
    font = _font(size)
    y = 90
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
        y += (bb[3] - bb[1]) + 10
    return im


def motion_scene(
    path: Path,
    seconds: float,
    fps: int,
    effect: str,
    lines: list[str] | None = None,
    darken: float = 0.72,
) -> list[Image.Image]:
    """
    effect: zoom_in | zoom_out | pan_down | pan_up | pan_right | pan_left | drift_zoom
    """
    big = _prepare_source(Image.open(path))
    max_x = max(0, big.width - W)
    max_y = max(0, big.height - H)
    n = max(2, int(seconds * fps))
    frames: list[Image.Image] = []

    for i in range(n):
        t = _ease(i / (n - 1))
        if effect == "zoom_in":
            # encuadre amplio → acercamiento al centro
            z = 1.0 - 0.28 * t
            cw, ch = int(big.width * z), int(big.height * z)
            resized = big.resize((cw, ch), Image.Resampling.LANCZOS)
            left = (resized.width - W) // 2
            top = (resized.height - H) // 2
            frame = _crop_window(resized, max(0, left), max(0, top))
        elif effect == "zoom_out":
            z = 0.72 + 0.28 * t
            cw, ch = int(big.width * z), int(big.height * z)
            resized = big.resize((cw, ch), Image.Resampling.LANCZOS)
            left = (resized.width - W) // 2
            top = (resized.height - H) // 2
            frame = _crop_window(resized, max(0, left), max(0, top))
        elif effect == "pan_down":
            # arranca arriba (tribunas) baja hacia la hinchada
            left = max_x // 6
            top = int(max_y * 0.15 * (1 - t) + max_y * 0.55 * t)
            top = min(top, max_y)
            frame = _crop_window(big, left, top)
        elif effect == "pan_up":
            left = max_x // 2
            top = int(max_y * (1 - t))
            frame = _crop_window(big, left, min(top, max_y))
        elif effect == "pan_right":
            top = max_y // 5
            left = int(max_x * t * 0.85)
            frame = _crop_window(big, min(left, max_x), top)
        elif effect == "pan_left":
            top = max_y // 4
            left = int(max_x * (1 - t) * 0.85)
            frame = _crop_window(big, min(left, max_x), top)
        elif effect == "drift_zoom":
            # paneo diagonal suave + zoom (ideal grupo / parque)
            z = 1.0 - 0.18 * t
            cw, ch = int(big.width * z), int(big.height * z)
            resized = big.resize((cw, ch), Image.Resampling.LANCZOS)
            mx = max(0, resized.width - W)
            my = max(0, resized.height - H)
            left = int(mx * 0.2 * t)
            top = int(my * 0.1 * (1 - t))
            frame = _crop_window(resized, left, top)
        else:
            frame = _crop_window(big, max_x // 2, max_y // 2)

        frame = _vignette(ImageEnhance.Brightness(frame).enhance(darken))
        if lines and i > n // 5:
            frame = _overlay_text(frame, lines)
        frames.append(frame)
    return frames


def text_card(lines: list[str], seconds: float, fps: int, bg=(6, 16, 12)) -> list[Image.Image]:
    n = max(1, int(seconds * fps))
    base = Image.new("RGB", (W, H), bg)
    base = _overlay_text(base, lines, 52)
    return [base.copy() for _ in range(n)]


def crossfade(a: Image.Image, b: Image.Image, steps: int = 10) -> list[Image.Image]:
    out = []
    for i in range(steps):
        t = (i + 1) / steps
        out.append(Image.blend(a, b, t))
    return out


def join_scenes(parts: list[list[Image.Image]], fade_frames: int = 8) -> list[Image.Image]:
    if not parts:
        return []
    out = list(parts[0])
    for nxt in parts[1:]:
        if fade_frames > 0 and out and nxt:
            tail = out[-1]
            head = nxt[0]
            blend = crossfade(tail, head, fade_frames)
            out = out[:-1] + blend + nxt[fade_frames:]
        else:
            out.extend(nxt)
    return out
