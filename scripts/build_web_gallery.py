"""
Copia y optimiza fotos curadas de archivos multimedia/ → frontend/public/media/galeria/
Ejecutar desde la raíz del repo: python scripts/build_web_gallery.py
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO / "archivos multimedia" / "fotos terra natura"
OUT_DIR = REPO / "frontend" / "public" / "media" / "galeria"
MAX_WIDTH = 1400
JPEG_QUALITY = 85

# Curado editorial — (slug, ruta relativa dentro de fotos terra natura, rol)
CURATED: list[tuple[str, str, str]] = [
    ("hero", "PARQUE/FOTO PANORAMICA DE NUESTRAS CABANAS.jpg", "hero"),
    ("01-complejo-panoramica", "exteriores cabanas/FRENTE DEL COMPLEJO.jpg", "complejo"),
    ("02-piscina", "PISCINA/NUESTRA PISCINA.jpg", "amenity"),
    ("03-pileta-alpina", "exteriores cabanas/reposera pileta y alpina.jpeg", "lifestyle"),
    (
        "04-alpina-vista-puerta",
        "CABANA ALPINA 1/VISTA PANORAMICA DESDE LA PUERTA DE LA CABANA.jpg",
        "alpina",
    ),
    (
        "05-alpina-living",
        "CABANA ALPINA 1/LIVING COMEDOR CABANA ALPINA CON 2 CAMAS DE 1 PLAZA.jpeg",
        "alpina",
    ),
    (
        "06-suite5-ventanal",
        "CABANA SUITE 5/HERMOSO VENTANAL CON VISTA A LAS SIERRAS DE CABANA SUITE PLANTA ALTA.jpg",
        "suite-5",
    ),
    ("07-suite4-interior", "CABANA SUITE 4/INTERIOR CABANA SUITE PB.jpg", "suite-4"),
    (
        "08-suites-exterior",
        "exteriores cabanas/VISTA EXTERIOR DE CABANAS SUITES.jpg",
        "suites",
    ),
    (
        "09-alpina-frente-pileta",
        "exteriores cabanas/VISTA EXTERIOR ALPINA FRENTE A PISCINA.jpg",
        "alpina",
    ),
    ("10-parque-mate", "exteriores cabanas/TOMANDO MATE EN EL PARQUE.jpg", "parque"),
    (
        "11-lago-plaza",
        "RIO Y BALNEARIOS/vista del lago desde la plaza federal caminata a  1km del complejo.jpg",
        "entorno",
    ),
    (
        "12-arroyo-cercano",
        "RIO Y BALNEARIOS/arroyo las mojarras cerquita del complejo.jpg",
        "entorno",
    ),
    (
        "13-parque-relax",
        "PARQUE/relax disfrutando una buena lectura y una rica copa.jpg",
        "parque",
    ),
]

# Tarjetas unidades en home
UNIT_IMAGES = {
    "alpina": "04-alpina-vista-puerta.jpg",
    "suite-4": "07-suite4-interior.jpg",
    "suite-5": "06-suite5-ventanal.jpg",
}


def _resize_save(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB") if im.mode not in ("RGB", "L") else im
        if im.mode == "L":
            im = im.convert("RGB")
        w, h = im.size
        if w > MAX_WIDTH:
            nh = int(h * MAX_WIDTH / w)
            im = im.resize((MAX_WIDTH, nh), Image.Resampling.LANCZOS)
        im.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)


def main() -> int:
    if not SRC_ROOT.is_dir():
        print(f"No existe carpeta origen: {SRC_ROOT}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_items: list[dict] = []
    missing: list[str] = []

    for slug, rel, rol in CURATED:
        src = SRC_ROOT / rel
        dest = OUT_DIR / f"{slug}.jpg"
        if not src.is_file():
            missing.append(rel)
            continue
        _resize_save(src, dest)
        manifest_items.append(
            {
                "id": slug,
                "archivo": f"media/galeria/{slug}.jpg",
                "rol": rol,
                "origen": rel.replace("\\", "/"),
            }
        )
        print(f"OK {slug} <- {rel}")

    manifest = {
        "version": 1,
        "items": manifest_items,
        "unidades": {
            "alpina": {"imagen": f"media/galeria/{UNIT_IMAGES['alpina']}"},
            "suite-4": {"imagen": f"media/galeria/{UNIT_IMAGES['suite-4']}"},
            "suite-5": {"imagen": f"media/galeria/{UNIT_IMAGES['suite-5']}"},
        },
    }
    json_path = REPO / "frontend" / "public" / "assets" / "data" / "galeria.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if missing:
        print("FALTAN:", *missing, sep="\n  ")
        return 2
    print(f"Listo: {len(manifest_items)} imágenes en {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
