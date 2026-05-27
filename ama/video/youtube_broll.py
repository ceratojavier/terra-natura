"""
Biblioteca B-roll YouTube — descarga fragmentos para montaje editorial Terra Natura.
Requiere: yt-dlp, ffmpeg, YOUTUBE_API_KEY (búsqueda si no hay id en cache/BD).
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent
CACHE = Path(__file__).resolve().parent.parent / "output" / "broll_cache"
SEGMENTS = Path(__file__).resolve().parent.parent / "output" / "broll_segments"

W, H = 1080, 1920
FPS = 30


def _ffmpeg() -> str:
    f = shutil.which("ffmpeg")
    if not f:
        raise RuntimeError("Instalá ffmpeg en el PATH.")
    return f


def _ytdlp() -> str:
    exe = shutil.which("yt-dlp")
    if exe:
        return exe
    import sys

    return f'"{sys.executable}" -m yt_dlp'


def parse_youtube_id(url_or_id: str) -> str | None:
    s = (url_or_id or "").strip()
    if not s:
        return None
    if re.fullmatch(r"[\w-]{11}", s):
        return s
    m = re.search(r"(?:v=|youtu\.be/|embed/)([\w-]{11})", s)
    return m.group(1) if m else None


def _cache_path(youtube_id: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / f"{youtube_id}.mp4"


def descargar_fuente(youtube_id: str) -> Path:
    """Descarga MP4 completo (máx 720p) y cachea por id."""
    dest = _cache_path(youtube_id)
    if dest.is_file() and dest.stat().st_size > 50_000:
        return dest
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    cmd = [
        shutil.which("yt-dlp") or "yt-dlp",
        "-f",
        "bv*[height<=720][ext=mp4]+ba/b[height<=720]/best[height<=720]",
        "--merge-output-format",
        "mp4",
        "--no-playlist",
        "-o",
        str(dest),
        url,
    ]
    if not shutil.which("yt-dlp"):
        import sys

        cmd = [
            sys.executable,
            "-m",
            "yt_dlp",
            "-f",
            "best[height<=720][ext=mp4]/best[height<=720]",
            "--merge-output-format",
            "mp4",
            "--no-playlist",
            "-o",
            str(dest),
            url,
        ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        partial = list(CACHE.glob(f"{youtube_id}.*"))
        if partial and partial[0].is_file():
            if partial[0] != dest:
                partial[0].rename(dest)
            return dest
        raise RuntimeError(f"yt-dlp: {(r.stderr or r.stdout)[-1500:]}")
    if not dest.is_file():
        hits = list(CACHE.glob(f"{youtube_id}*"))
        if hits:
            return hits[0]
    return dest


def _probe_duration(path: Path) -> float:
    ff = _ffmpeg()
    r = subprocess.run(
        [ff, "-i", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)", r.stderr or "")
    if not m:
        return 120.0
    h, mi, s, cs = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(s) + int(cs) / 100.0


def _start_offset(total: float, seed: str) -> float:
    """Evita intro/outro — punto estable por video."""
    h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
    if total < 25:
        return min(2.0, max(0.5, total * 0.1))
    margin = min(20.0, total * 0.15)
    usable = max(10.0, total - margin * 2)
    return margin + (h % int(usable * 10)) / 10.0


def extraer_segmento_vertical(
    youtube_id: str,
    dest: Path,
    *,
    duracion: float = 4.5,
    inicio: float | None = None,
) -> Path:
    """
    Fragmento vertical 1080x1920, sin audio (va música del reel).
    """
    SEGMENTS.mkdir(parents=True, exist_ok=True)
    src = descargar_fuente(youtube_id)
    total = _probe_duration(src)
    start = inicio if inicio is not None else _start_offset(total, youtube_id)
    start = max(0.0, min(start, max(0.0, total - duracion - 0.5)))
    dest.parent.mkdir(parents=True, exist_ok=True)

    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"eq=contrast=1.06:brightness=0.02:saturation=1.12,"
        f"fade=t=in:st=0:d=0.35,fade=t=out:st={max(0.1, duracion - 0.45)}:d=0.4,"
        f"format=yuv420p"
    )
    cmd = [
        _ffmpeg(),
        "-y",
        "-ss",
        str(start),
        "-t",
        str(duracion),
        "-i",
        str(src),
        "-vf",
        vf,
        "-r",
        str(FPS),
        "-an",
        "-c:v",
        "libx264",
        "-crf",
        "19",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-2000:])
    return dest


def buscar_broll_id(
    query: str,
    db: Any | None = None,
    *,
    preferidos: list[dict] | None = None,
) -> str | None:
    """Resuelve youtube_id: assets del calendario → BD → API search."""
    if preferidos:
        for c in preferidos:
            yid = parse_youtube_id(c.get("youtube_id") or c.get("url") or c.get("fuente", ""))
            if yid:
                return yid

    if db is not None:
        try:
            from backend.models.turismo import TurismoContenido

            rows = (
                db.query(TurismoContenido)
                .filter(
                    TurismoContenido.youtube_id.isnot(None),
                    TurismoContenido.plataforma == "youtube",
                )
                .all()
            )
            q = query.lower()
            for row in rows:
                blob = f"{row.titulo} {row.localidad} {row.notas or ''}".lower()
                if any(w in blob for w in q.split() if len(w) > 3):
                    return row.youtube_id
            if rows:
                return rows[0].youtube_id
        except Exception:
            pass

    try:
        from backend.config.settings import YOUTUBE_API_KEY
        from backend.services.youtube_turismo import buscar_youtube

        if YOUTUBE_API_KEY and len(YOUTUBE_API_KEY) > 20:
            hits = buscar_youtube(YOUTUBE_API_KEY, query, 3)
            if hits:
                return hits[0]["youtube_id"]
    except Exception:
        pass
    return None


def obtener_segmento_broll(
    *,
    youtube_id: str | None = None,
    broll_query: str | None = None,
    duracion: float = 4.5,
    work_dir: Path,
    db: Any | None = None,
    preferidos: list[dict] | None = None,
    slug: str = "scene",
) -> Path | None:
    yid = youtube_id or buscar_broll_id(
        broll_query or "sierras Cordoba naturaleza lago", db, preferidos=preferidos
    )
    if not yid:
        return None
    dest = work_dir / f"broll_{slug}_{yid[:8]}.mp4"
    if dest.is_file() and dest.stat().st_size > 10_000:
        return dest
    try:
        return extraer_segmento_vertical(yid, dest, duracion=duracion)
    except Exception:
        return None
