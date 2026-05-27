"""
Importa fotos que pegás en el chat (carpeta Cursor assets) → propias / propias_river.
Clasifica por color dominante (celeste = Belgrano, rojo = River).

python -m ama.video.import_fotos_chat
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from PIL import Image

CURSOR_ASSETS = Path(
    r"C:\Users\Usuario\.cursor\projects\c-Users-Usuario-Desktop-proyectos-programacion-Proyecto-Terra-Natura\assets"
)
BASE = Path(__file__).resolve().parent.parent / "output" / "assets"
BELGRANO = BASE / "propias"
RIVER = BASE / "propias_river"
SKIP_NAMES = {"belgrano_hinchada_atmosfera.png"}


def _long(path: str | Path) -> str:
    p = os.path.abspath(str(path))
    if os.name == "nt" and not p.startswith("\\\\?\\"):
        p = "\\\\?\\" + p
    return p


def _dominant_scores(path: Path) -> tuple[float, float]:
    """Retorna (score_celeste, score_rojo)."""
    im = Image.open(path).convert("RGB").resize((160, 160))
    celeste = rojo = 0
    for r, g, b in im.getdata():
        if b > r + 25 and b > g + 10:
            celeste += 1
        if r > 140 and r > g + 30 and r > b + 30:
            rojo += 1
    n = max(len(im.getdata()), 1)
    return celeste / n, rojo / n


def _hint_from_name(name: str) -> str | None:
    low = name.lower()
    if "river" in low or "descarga-a4c1" in low:
        return "river"
    if any(x in low for x in ("belgrano", "hq720", "pirata", "celeste", "8fd28df3", "la14", "alberdi")):
        return "belgrano"
    if "foto-principal" in low or "kempes" in low:
        return "both"
    return None


def _next_name(folder: Path, prefix: str, ext: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    n = 1
    while True:
        cand = folder / f"{prefix}{n:02d}{ext}"
        if not cand.exists():
            return cand
        n += 1


def import_all() -> dict[str, list[str]]:
    imported: dict[str, list[str]] = {"belgrano": [], "river": []}
    if not CURSOR_ASSETS.is_dir():
        print("No hay carpeta de fotos del chat:", CURSOR_ASSETS)
        return imported

    for name in os.listdir(str(CURSOR_ASSETS)):
        if name in SKIP_NAMES:
            continue
        low = name.lower()
        if not low.endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue
        src = Path(_long(CURSOR_ASSETS / name))
        try:
            if src.stat().st_size < 4000:
                continue
        except OSError:
            continue

        hint = _hint_from_name(name)
        celeste, rojo = _dominant_scores(src)
        if hint == "river" or (hint is None and rojo > celeste * 1.15 and rojo > 0.08):
            dest_dir = RIVER
            team = "river"
        elif hint == "belgrano" or celeste >= rojo:
            dest_dir = BELGRANO
            team = "belgrano"
        else:
            dest_dir = RIVER
            team = "river"

        ext = Path(name).suffix.lower() or ".jpg"
        # Evitar duplicar: mismo tamaño ya copiado
        size = src.stat().st_size
        dup = any(
            f.stat().st_size == size and f.suffix.lower() == ext
            for f in dest_dir.iterdir()
            if f.is_file()
        )
        if dup:
            continue
        dest = _next_name(dest_dir, "", ext)
        shutil.copy2(_long(src), _long(dest))
        imported[team].append(dest.name)
        print(f"  {team}: {dest.name} ({src.stat().st_size // 1024} KB)")

    return imported


if __name__ == "__main__":
    print("Importando fotos del chat...")
    r = import_all()
    print("Belgrano:", len(r["belgrano"]), "| River:", len(r["river"]))
