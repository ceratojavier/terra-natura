"""
Reel cinematográfico: B-roll YouTube (biblioteca) + fotos Terra Natura + diseño marca.
Montaje por segmentos con fundidos — no pega un clip crudo con foto encima.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ama.video.brand_frames import (
    FPS,
    cta_card,
    hook_card,
    join_scenes,
    photo_scene,
)
from ama.video.youtube_broll import (
    obtener_segmento_broll,
    parse_youtube_id,
)

REPO = Path(__file__).resolve().parent.parent.parent
MEDIA = REPO / "archivos multimedia"
OUT = REPO / "ama" / "output" / "videos" / "editorial"
VISIBLE = MEDIA / "videos marketing" / "editorial"
WORK = Path(__file__).resolve().parent.parent / "output" / "reel_work"

CTA_LINES = ["Terra Natura", "Bialet Massé · Córdoba", "Reservá por WhatsApp"]


def _ffmpeg() -> str:
    f = shutil.which("ffmpeg")
    if not f:
        raise RuntimeError("Instalá ffmpeg y agregalo al PATH.")
    return f


def _find_music() -> Path | None:
    from ama.storage.calendar_store import get_config

    cfg = get_config()
    custom = cfg.get("musica_fondo_ruta")
    if custom:
        p = REPO / str(custom).replace("\\", "/")
        if p.is_file():
            return p
    for base in (
        MEDIA / "recursos de la marca",
        REPO / "ama" / "assets" / "music",
    ):
        if not base.is_dir():
            continue
        for ext in ("*.mp3", "*.m4a", "*.wav", "*.aac"):
            found = list(base.glob(ext))
            if found:
                return found[0]
    return None


def _resolve_photo(fuente: str) -> Path | None:
    if not fuente:
        return None
    p = REPO / fuente.replace("\\", "/")
    if p.is_file():
        return p
    p2 = MEDIA / fuente.replace("\\", "/")
    if p2.is_file():
        return p2
    name = Path(fuente).name
    for hit in MEDIA.rglob(name):
        if hit.is_file():
            return hit
    return None


def _frames_to_mp4(frames: list, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, fr in enumerate(frames):
            fr.save(tmp_path / f"f_{i:06d}.jpg", quality=92)
        r = subprocess.run(
            [
                _ffmpeg(),
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(tmp_path / "f_%06d.jpg"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-crf",
                "20",
                "-preset",
                "fast",
                str(dest),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout)[-2000:])


def _probe_seg_duration(path: Path) -> float:
    from ama.video.youtube_broll import _probe_duration

    try:
        return max(0.5, float(_probe_duration(path)))
    except Exception:
        return 3.5


def _concat_segments(segments: list[Path], dest: Path, *, xfade_sec: float = 0.45) -> None:
    """Une escenas con fundido cruzado (armónico). Fallback: concat duro."""
    segs = [s for s in segments if s.is_file()]
    if not segs:
        raise RuntimeError("Sin segmentos para unir")
    if len(segs) == 1:
        shutil.copy2(segs[0], dest)
        return

    durs = [_probe_seg_duration(s) for s in segs]
    ff = _ffmpeg()
    inputs: list[str] = []
    for s in segs:
        inputs += ["-i", str(s.resolve())]

    # Cadena xfade: evita corte brusco foto ↔ YouTube
    fade = max(0.25, min(xfade_sec, min(durs) * 0.35))
    parts: list[str] = []
    prev = "[0:v]"
    offset = durs[0] - fade
    for i in range(1, len(segs)):
        out = f"[v{i}]" if i < len(segs) - 1 else "[vout]"
        parts.append(
            f"{prev}[{i}:v]xfade=transition=fade:duration={fade:.3f}:offset={max(0.1, offset):.3f}{out}"
        )
        prev = out
        offset += durs[i] - fade

    fc = ";".join(parts)
    cmd = [ff, "-y", *inputs, "-filter_complex", fc, "-map", "[vout]", "-an", "-c:v", "libx264", "-crf", "19", "-preset", "fast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0 and dest.is_file():
        return

    lst = dest.parent / "concat_list.txt"
    lst.write_text(
        "\n".join(f"file '{s.resolve().as_posix()}'" for s in segs),
        encoding="utf-8",
    )
    r2 = subprocess.run(
        [
            ff,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-c:v",
            "libx264",
            "-crf",
            "19",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(dest),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r2.returncode != 0:
        raise RuntimeError((r2.stderr or r2.stdout or r.stderr or "")[-2000:])


def _write_ass(path: Path, blocks: list[tuple[float, float, str, str]]) -> None:
    """blocks: (start, end, main, sub opcional)"""
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Alignment, MarginV
Style: Main,Arial,54,&H00F8F5FF,&H00000000,&H90000000,-1,2,110,1
Style: Sub,Arial,40,&H00D4B48A,&H00000000,&H80000000,0,2,170,1

[Events]
Format: Layer, Start, End, Style, Text
"""
    lines = [header]

    def ts(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        cs = int((sec % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    for start, end, main, sub in blocks:
        main = main.replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Main,{main}")
        if sub:
            sub_t = sub.replace("\n", "\\N")
            lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Sub,{sub_t}")
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def _split_voz(voz: str, n: int) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", voz.strip())
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) >= n:
        return parts[:n]
    while len(parts) < n and parts:
        parts.append(parts[-1])
    return parts or [voz[:90]]


def _mux_final(video: Path, audio: Path | None, ass: Path | None, dest: Path) -> None:
    ff = _ffmpeg()
    cmd = [ff, "-y", "-i", str(video)]
    if audio and audio.is_file():
        cmd += ["-i", str(audio)]
    vf = []
    if ass and ass.is_file():
        ap = ass.resolve().as_posix().replace(":", "\\:")
        vf.append(f"subtitles='{ap}'")
    if vf:
        cmd += ["-vf", ",".join(vf)]
    cmd += ["-map", "0:v"]
    if audio and audio.is_file():
        cmd += ["-map", "1:a", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-preset", "medium"]
    if audio and audio.is_file():
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-an"]
    cmd += ["-movflags", "+faststart", str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-2000:])


def _render_escena(
    esc: dict,
    idx: int,
    work: Path,
    *,
    db: Any | None,
    yt_preferidos: list[dict],
    photo_pool: list[Path],
) -> tuple[Path | None, float, tuple[float, float, str, str] | None]:
    """Devuelve (segmento mp4, duración, bloque subtítulo)."""
    tipo = esc.get("tipo", "")
    dur = float(esc.get("duracion_seg", 3.5))
    lineas = esc.get("lineas") or []
    main_sub = (
        " ".join(lineas[:1]) if lineas else "",
        " ".join(lineas[1:2]) if len(lineas) > 1 else "",
    )

    if tipo == "hook_card":
        frames = hook_card(esc.get("lineas") or ["Terra Natura"], dur)
        out = work / f"{idx:02d}_hook.mp4"
        _frames_to_mp4(frames, out)
        sub = (0.0, dur, main_sub[0] or "Terra Natura", main_sub[1])
        return out, dur, sub

    if tipo == "cierre":
        frames = cta_card(esc.get("lineas") or CTA_LINES, dur)
        out = work / f"{idx:02d}_cierre.mp4"
        _frames_to_mp4(frames, out)
        sub = (0.0, dur, "Reservá por WhatsApp", "Terra Natura · Bialet")
        return out, dur, sub

    if tipo in ("broll_youtube", "clip_youtube"):
        yid = parse_youtube_id(
            esc.get("youtube_id") or esc.get("fuente") or ""
        )
        seg = obtener_segmento_broll(
            youtube_id=yid,
            broll_query=esc.get("broll_query"),
            duracion=dur,
            work_dir=work,
            db=db,
            preferidos=yt_preferidos,
            slug=f"{idx}_{esc.get('broll_tipo', 'sc')}",
        )
        if seg and seg.is_file():
            sub = (0.0, dur, main_sub[0] or "Escapada a las sierras", main_sub[1])
            return seg, dur, sub
        # fallback foto si no hay yt-dlp o falla descarga
        tipo = "foto"

    if tipo == "foto":
        fuente = esc.get("fuente", "")
        path = _resolve_photo(fuente) if fuente else None
        if not path and photo_pool:
            path = photo_pool[idx % len(photo_pool)]
        if not path:
            return None, 0.0, None
        frames = photo_scene(
            path,
            dur,
            esc.get("effect", "zoom_in"),
            list(lineas) if lineas else None,
        )
        out = work / f"{idx:02d}_foto.mp4"
        _frames_to_mp4(frames, out)
        sub = (0.0, dur, main_sub[0], main_sub[1])
        return out, dur, sub

    return None, 0.0, None


def build_from_guion(
    guion: dict,
    *,
    assets: dict | None = None,
    pub_id: str | None = None,
    objetivo: str | None = None,
    db: Any | None = None,
) -> dict:
    assets = assets or {}
    objetivo = objetivo or guion.get("objetivo") or "branding"
    yt_preferidos = assets.get("youtube_clips") or []

    photo_paths: list[Path] = []
    for f in assets.get("fotos") or []:
        p = _resolve_photo(f)
        if p:
            photo_paths.append(p)
    for esc in guion.get("escenas") or []:
        if esc.get("tipo") == "foto":
            p = _resolve_photo(esc.get("fuente", ""))
            if p and p not in photo_paths:
                photo_paths.append(p)

    if not photo_paths and not yt_preferidos:
        return {
            "ok": False,
            "ruta": None,
            "mensaje": "Sin fotos ni referencias YouTube. Ejecutá Recolectar-videos-YouTube.bat y agregá fotos.",
        }

    slug = (pub_id or objetivo)[:12].replace(" ", "_")
    fname = f"TN_{guion.get('canal', 'reel')}_{slug}.mp4"
    OUT.mkdir(parents=True, exist_ok=True)
    VISIBLE.mkdir(parents=True, exist_ok=True)
    dest = OUT / fname
    work = WORK / f"job_{slug}"
    if work.is_dir():
        shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)

    segments: list[Path] = []
    ass_blocks: list[tuple[float, float, str, str]] = []
    t_cursor = 0.0
    broll_usados = 0

    escenas = guion.get("escenas") or []
    if not escenas:
        return {"ok": False, "mensaje": "Guion sin escenas"}

    for i, esc in enumerate(escenas):
        seg, dur, sub = _render_escena(
            esc, i, work, db=db, yt_preferidos=yt_preferidos, photo_pool=photo_paths
        )
        if seg and seg.is_file():
            segments.append(seg)
            if esc.get("tipo") in ("broll_youtube", "clip_youtube"):
                broll_usados += 1
            if sub:
                ass_blocks.append((t_cursor, t_cursor + dur, sub[2], sub[3]))
            t_cursor += dur

    if not segments:
        return {"ok": False, "mensaje": "No se pudo renderizar ningún segmento (ffmpeg / yt-dlp)."}

    raw = work / "concat.mp4"
    xfade = float(guion.get("xfade_seg") or 0.45)
    _concat_segments(segments, raw, xfade_sec=xfade)

    ass = work / "subs.ass"
    voz = guion.get("voz_off") or ""
    if voz and len(ass_blocks) < 3:
        chunks = _split_voz(voz, 4)
        slot = t_cursor / max(1, len(chunks))
        ass_blocks = []
        tt = 0.3
        for ch in chunks:
            ass_blocks.append((tt, min(tt + slot, t_cursor - 0.2), ch, ""))
            tt += slot
    else:
        # Ajustar tiempos absolutos en ass_blocks (ya están bien)
        pass

    _write_ass(ass, ass_blocks)
    music = _find_music()
    _mux_final(raw, music, ass, dest)

    shutil.copy2(dest, VISIBLE / fname)
    rel = str(dest.relative_to(REPO)).replace("\\", "/")

    return {
        "ok": True,
        "ruta": rel,
        "ruta_visible": str((VISIBLE / fname).relative_to(REPO)).replace("\\", "/"),
        "mensaje": (
            f"Video listo ({int(t_cursor)} s) · B-roll YouTube: {broll_usados} · "
            f"Fotos: {len(photo_paths)} · Música: {'sí' if music else 'opcional en ama/assets/music/'}"
        ),
        "duracion_seg": round(t_cursor, 1),
        "broll_segmentos": broll_usados,
        "musica": str(music) if music else None,
    }


def build_from_publicacion(pub: dict, db: Any | None = None) -> dict:
    guion = pub.get("guion")
    if isinstance(guion, str):
        try:
            guion = json.loads(guion)
        except json.JSONDecodeError:
            guion = None
    if not guion:
        return {"ok": False, "mensaje": "La publicación no tiene guion."}
    return build_from_guion(
        guion,
        assets=pub.get("assets"),
        pub_id=pub.get("id"),
        objetivo=pub.get("objetivo"),
        db=db,
    )


def build_lote_calendario(
    *,
    dias: int = 14,
    solo_reel: bool = True,
    max_videos: int = 5,
    db: Any | None = None,
) -> dict:
    from datetime import date, timedelta
    from ama.storage.calendar_store import actualizar_publicacion, list_publicaciones

    hasta = date.today() + timedelta(days=dias)
    pubs = list_publicaciones(desde=date.today(), hasta=hasta)
    candidatos = []
    for p in pubs:
        if p.get("video_ruta"):
            continue
        fmt = p.get("formato") or ""
        canal = p.get("canal") or ""
        if solo_reel and fmt != "reel" and canal not in ("instagram", "tiktok"):
            continue
        if p.get("guion"):
            candidatos.append(p)
    hechos = []
    errores = []
    for p in candidatos[:max_videos]:
        r = build_from_publicacion(p, db=db)
        if r.get("ok") and p.get("id"):
            actualizar_publicacion(p["id"], {"video_ruta": r["ruta"]})
            hechos.append({"id": p["id"], "fecha": p.get("fecha_publicacion"), "ruta": r["ruta"]})
        else:
            errores.append({"id": p.get("id"), "error": r.get("mensaje")})
    return {"ok": True, "generados": len(hechos), "videos": hechos, "errores": errores}
