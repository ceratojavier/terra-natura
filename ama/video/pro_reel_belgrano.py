"""
Reel vertical 1080x1920 — Belgrano final Kempes + Terra Natura.
Usa clips 1080p del usuario (hinchada real) + fotos HD de cabañas + música emotiva.

python -m ama.video.audit_calidad
python -m ama.video.pro_reel_belgrano
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "ama" / "output" / "videos"
WORK = REPO / "ama" / "output" / "reel_work"
FOTOS = REPO / "archivos multimedia" / "fotos terra natura"

W, H = 1080, 1920
FPS = 30
# Pillow para titulares (drawtext de ffmpeg falla con rutas Windows)

CLIP_PUBLICO = Path(
    r"c:\Users\Usuario\Downloads\YTDown_YouTube_Belgrano-record-de-publico-en-el-Kempes-_Media_bgeSTx6EQgc_001_1080p.mp4"
)
AUDIO_SRC = Path(
    r"c:\Users\Usuario\Downloads\YTDown_YouTube_La-Fiesta-de-Belgrano-Campeon-para-la-hi_Media_WmXHV64WE3I_001_1080p.mp4"
)

# Solo archivos con resolución usable en vertical (audit)
CABANAS = [
    (
        "exteriores cabanas/FRENTE DEL COMPLEJO.jpg",
        "Cabañas Alpinas Terra Natura",
        "Los Talas 759 · Bialet Massé",
        5.0,
        "in",
    ),
    (
        "PISCINA/RELAX EN LA PISCINA.jpg",
        "Pileta · parque · descanso",
        "Después del Kempes",
        4.5,
        "in",
    ),
    (
        "exteriores cabanas/FRENTE DEL COMPLEJO.jpg",
        "Reservá tu finde",
        "WhatsApp 3541 571190",
        4.0,
        "in",
    ),
]


def _ffmpeg() -> str:
    f = shutil.which("ffmpeg")
    if not f:
        raise SystemExit("Instalá ffmpeg.")
    return f


def _run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout)[-2500:])


def _clip_vertical(src: Path, dest: Path, start: float, dur: float) -> None:
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},fps={FPS},format=yuv420p"
    )
    _run(
        [
            _ffmpeg(),
            "-y",
            "-ss",
            str(start),
            "-t",
            str(dur),
            "-i",
            str(src),
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            str(dest),
        ]
    )


def _photo_reel(path: Path, dest: Path, seconds: float, zoom: str = "in") -> None:
    frames = max(1, int(seconds * FPS))
    if zoom == "in":
        zexpr = "min(zoom+0.0010,1.35)"
    else:
        zexpr = "if(lte(zoom,1.0),1.35,max(1.001,zoom-0.0010))"
    vf = (
        f"scale=2160:3840:force_original_aspect_ratio=increase,"
        f"crop=2160:3840,"
        f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p"
    )
    _run(
        [
            _ffmpeg(),
            "-y",
            "-loop",
            "1",
            "-i",
            str(path),
            "-vf",
            vf,
            "-t",
            str(seconds),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            str(dest),
        ]
    )


def _title_card(dest: Path, line1: str, line2: str, seconds: float) -> None:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (W, H), (10, 24, 18))
    draw = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype("arialbd.ttf", 72)
        f2 = ImageFont.truetype("arial.ttf", 48)
    except OSError:
        f1 = f2 = ImageFont.load_default()

    def centered(text: str, y: int, font, fill):
        bb = draw.textbbox((0, 0), text, font=font, stroke_width=4)
        tw = bb[2] - bb[0]
        draw.text(((W - tw) // 2, y), text, fill=fill, font=font, stroke_width=4, stroke_fill=(0, 0, 0))

    centered(line1, int(H * 0.38), f1, (255, 255, 255))
    centered(line2, int(H * 0.48), f2, (138, 212, 255))
    tmp = dest.with_suffix(".png")
    img.save(tmp, quality=95)
    fade_out = max(0.2, seconds - 0.5)
    vf = f"format=yuv420p,fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out}:d=0.5"
    _run(
        [
            _ffmpeg(),
            "-y",
            "-loop",
            "1",
            "-i",
            str(tmp),
            "-vf",
            vf,
            "-t",
            str(seconds),
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ]
    )
    tmp.unlink(missing_ok=True)


def _write_ass(path: Path, blocks: list[tuple[float, str, str]]) -> None:
    def ts(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        cs = int(round((s % 1) * 100))
        return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"

    body = [
        "[Script Info]",
        "Title: Terra Natura",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Main,Arial,56,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,4,2,2,50,50,120,1",
        "Style: Sub,Arial,40,&H00FFD48A,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,50,50,175,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    t = 0.0
    for dur, main, sub in blocks:
        body.append(f"Dialogue: 0,{ts(t)},{ts(t + dur)},Main,,0,0,0,,{main}")
        if sub:
            body.append(f"Dialogue: 0,{ts(t)},{ts(t + dur)},Sub,,0,0,0,,{sub}")
        t += dur
    path.write_text("\n".join(body), encoding="utf-8-sig")


def _concat(segments: list[Path], dest: Path) -> None:
    lst = dest.parent / "concat.txt"
    lst.write_text("\n".join(f"file '{s.resolve().as_posix()}'" for s in segments), encoding="utf-8")
    _run(
        [
            _ffmpeg(),
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-c",
            "copy",
            str(dest),
        ]
    )


def build() -> Path:
    if not CLIP_PUBLICO.is_file():
        raise SystemExit(f"Falta clip hinchada: {CLIP_PUBLICO}")
    if not AUDIO_SRC.is_file():
        raise SystemExit(f"Falta música: {AUDIO_SRC}")

    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    segments: list[Path] = []
    subs: list[tuple[float, str, str]] = []

    s0 = WORK / "00_hook.mp4"
    _title_card(s0, "FINAL EN EL KEMPES", "Belgrano en Cordoba", 2.4)
    segments.append(s0)
    subs.append((2.4, "FINAL EN EL KEMPES", "Belgrano · Córdoba"))

    s1 = WORK / "01_hinchada.mp4"
    _clip_vertical(CLIP_PUBLICO, s1, start=3.0, dur=7.0)
    segments.append(s1)
    subs.append((7.0, "La hinchada lo siente", "Estadio Kempes"))

    s2 = WORK / "02_puente.mp4"
    _title_card(s2, "Después del grito", "Tu lugar en Bialet Massé", 2.0)
    segments.append(s2)
    subs.append((2.0, "Después del partido", "Bialet Massé · Punilla"))

    for i, (rel, main, sub, sec, zoom) in enumerate(CABANAS):
        p = FOTOS / rel
        if not p.is_file():
            print("skip cabaña:", rel)
            continue
        out = WORK / f"10_cabana_{i:02d}.mp4"
        _photo_reel(p, out, sec, zoom)
        segments.append(out)
        subs.append((sec, main, sub))

    raw = WORK / "video_sin_audio.mp4"
    _concat(segments, raw)

    ass = WORK / "subs.ass"
    _write_ass(ass, subs)

    audio_trim = WORK / "audio.aac"
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(AUDIO_SRC),
            "-t",
            "42",
            "-vn",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(audio_trim),
        ]
    )

    dest = OUT / "kempes_belgrano_PRO_whatsapp.mp4"
    visible = REPO / "archivos multimedia" / "videos marketing"
    visible.mkdir(parents=True, exist_ok=True)
    ass_path = ass.resolve().as_posix().replace(":", "\\:")
    _run(
        [
            _ffmpeg(),
            "-y",
            "-i",
            str(raw),
            "-i",
            str(audio_trim),
            "-vf",
            f"subtitles='{ass_path}'",
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )
    shutil.copy2(dest, visible / dest.name)
    print(dest)
    print("Copia visible:", visible / dest.name)
    return dest


if __name__ == "__main__":
    build()
