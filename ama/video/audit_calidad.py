"""Audita fotos: resolución, nitidez, orientación."""
from __future__ import annotations

import os
import statistics
from pathlib import Path

from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parent.parent.parent


def long(p: Path) -> str:
    s = os.path.abspath(str(p))
    return "\\\\?\\" + s if os.name == "nt" and not s.startswith("\\\\?\\") else s


def audit(path: Path) -> list[str]:
    im = Image.open(long(path))
    w, h = im.size
    small = im.copy()
    small.thumbnail((500, 500))
    edges = small.convert("L").filter(ImageFilter.FIND_EDGES)
    sharp = statistics.pstdev(list(edges.getdata()))
    issues = []
    if w < 900 or h < 900:
        issues.append("BAJA_RES")
    if max(w, h) < 1400:
        issues.append("MUY_CHICA")
    if sharp < 14:
        issues.append("PIXELADA")
    if w > h * 1.2:
        issues.append("HORIZONTAL")
    tag = " | ".join(issues) if issues else "OK_USAR"
    print(f"  {w}x{h}  nitidez={sharp:.0f}  {tag}  {path.name}")
    return issues


if __name__ == "__main__":
    print("PROPIAS BELGRANO:")
    for f in sorted((REPO / "ama/output/assets/propias").glob("*")):
        if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            audit(f)
    poster = Path(
        r"C:\Users\Usuario\.cursor\projects\c-Users-Usuario-Desktop-proyectos-programacion-Proyecto-Terra-Natura\assets"
    )
    for f in poster.glob("*images__1_*"):
        print("POSTER CHAT:")
        audit(f)
    print("CABANAS:")
    base = REPO / "archivos multimedia" / "fotos terra natura"
    for rel in [
        "PARQUE/VISTA PANORAMICA DESDE EL COMPLEJO A TODO EL VALLE DE PUNILLA.jpg",
        "PISCINA/PARQUE Y PISCINA.jpg",
        "exteriores cabanas/FRENTE DEL COMPLEJO.jpg",
        "PISCINA/RELAX EN LA PISCINA.jpg",
    ]:
        p = base / rel
        if p.is_file():
            audit(p)
