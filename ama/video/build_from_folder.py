"""Arma video desde TODAS las fotos de una carpeta con efectos rotativos."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from ama.video.motion_effects import join_scenes, motion_scene, text_card

REPO = Path(__file__).resolve().parent.parent.parent
FOTOS = REPO / "archivos multimedia" / "fotos terra natura"
OUT = Path(__file__).resolve().parent.parent / "output" / "videos"
FPS = 30

EFFECTS = ("zoom_in", "pan_down", "drift_zoom", "pan_right", "zoom_out", "pan_left")

BELGRANO_TEXTS = [
    (["ESTE FINDE", "CÓRDOBA ES FÚTBOL"], "zoom_in"),
    (["LOS PIRATAS CELESTES", "BELGRANO EN EL KEMPES"], "pan_down"),
    (["¿Y SI BELGRANO", "ES CAMPEÓN", "POR PRIMERA VEZ?"], None),
    (["DESPUÉS DEL GRITO", "BIALET MASSÉ"], None),
]

RIVER_TEXTS = [
    (["FINAL EN EL KEMPES"], "zoom_in"),
    (["MILLONES DE HINCHAS", "EN CÓRDOBA"], "pan_right"),
    (["¿VENÍS DESDE", "BUENOS AIRES?"], None),
    (["DESPUÉS DEL PARTIDO", "BIALET MASSÉ"], None),
]

# Cierre estadía: partido en Kempes → tu base en Bialet (más tiempo en pantalla)
CABANA_BELGRANO = (
    (
        "exteriores cabanas/VISTA PANORAMICA DEL COMPLEJO.jpg",
        ["TU REFUGIO", "DESPUÉS DEL PARTIDO"],
        "zoom_in",
        4.5,
    ),
    (
        "PARQUE/VISTA PANORAMICA DESDE EL COMPLEJO A TODO EL VALLE DE PUNILLA.jpg",
        ["CABAÑAS ALPINAS TERRA NATURA", "Los Talas 759 · Bialet Massé"],
        "zoom_out",
        4.5,
    ),
    (
        "RIO Y BALNEARIOS/TOMANDO UNOS MATES EN LOS LABIOS DEL INDIO EN BIALET MASSE.jpg",
        ["A MINUTOS DEL LAGO Y EL RÍO"],
        "pan_right",
        3.8,
    ),
    (
        "PISCINA/RELAX EN LA PISCINA.jpg",
        ["PILETA · PARQUE · DESCANSO"],
        "drift_zoom",
        4.0,
    ),
    (
        "exteriores cabanas/FRENTE DEL COMPLEJO.jpg",
        ["RESERVÁ TU FINDE", "WhatsApp 3541 571190"],
        "zoom_in",
        4.5,
    ),
)

CABANA_RIVER = (
    (
        "exteriores cabanas/FRENTE DEL COMPLEJO.jpg",
        ["BASE EN BIALET MASSÉ", "SIN VOLVER A CAPITAL"],
        "zoom_in",
        4.5,
    ),
    (
        "PARQUE/VISTA PANORAMICA DESDE EL COMPLEJO A TODO EL VALLE DE PUNILLA.jpg",
        ["CABAÑAS ALPINAS TERRA NATURA", "Valle de Punilla"],
        "pan_left",
        4.2,
    ),
    (
        "PISCINA/RELAX EN LA PISCINA.jpg",
        ["RELAX DESPUÉS DEL PARTIDO"],
        "drift_zoom",
        4.0,
    ),
    (
        "PISCINA/PARQUE Y PISCINA.jpg",
        ["RESERVÁ TU FINDE", "WhatsApp 3541 571190"],
        "zoom_in",
        4.5,
    ),
)


def _list_fotos(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in folder.iterdir() if p.suffix.lower() in exts and p.stat().st_size > 8000]
    return sorted(files, key=lambda p: p.name)


def _resolve_local(rel: str) -> Path | None:
    p = FOTOS / rel
    return p if p.is_file() else None


def build_from_folder(
    folder: Path,
    team: str,
    out_name: str,
    card_bg: tuple[int, int, int],
) -> Path:
    fotos = _list_fotos(folder)
    if not fotos:
        raise SystemExit(f"No hay fotos en {folder}")

    texts = BELGRANO_TEXTS if team == "belgrano" else RIVER_TEXTS
    cabanas = CABANA_BELGRANO if team == "belgrano" else CABANA_RIVER
    scenes: list[list[Image.Image]] = []

    ti = 0
    for i, path in enumerate(fotos):
        if ti < len(texts) and texts[ti][1] is None:
            scenes.append(text_card(list(texts[ti][0]), 2.3, FPS, bg=card_bg))
            ti += 1
        lines: list[str] = []
        effect = EFFECTS[i % len(EFFECTS)]
        if ti < len(texts) and texts[ti][1] is not None:
            lines = list(texts[ti][0])
            effect = texts[ti][1] or effect
            ti += 1
        sec = 4.0 if i == 0 else 3.6
        scenes.append(motion_scene(path, sec, FPS, effect, lines, darken=0.76))

    if ti < len(texts):
        for j in range(ti, len(texts)):
            if texts[j][1] is None:
                scenes.append(text_card(list(texts[j][0]), 2.0, FPS, bg=card_bg))

    for item in cabanas:
        rel, txt, eff = item[0], item[1], item[2]
        sec = item[3] if len(item) > 3 else 4.0
        p = _resolve_local(rel)
        if p:
            scenes.append(motion_scene(p, sec, FPS, eff, list(txt), darken=0.88))
            print(f"  + cabaña: {rel}")

    frames = join_scenes(scenes, fade_frames=12)
    return _encode(frames, out_name)


def _encode(frames: list[Image.Image], filename: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / filename
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, fr in enumerate(frames):
            fr.save(tmp_path / f"f_{i:06d}.jpg", quality=93)
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
            text=True,
        )
    print(dest)
    return dest
