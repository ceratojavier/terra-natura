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
MAX_WIDTH = 1920
JPEG_QUALITY = 90

# slug, candidatos (primer archivo existente gana), rol
CURATED: list[tuple[str, list[str], str]] = [
    (
        "hero",
        [
            "PISCINA/PARQUE Y PISCINA.jpg",
            "CABAÑA ALPINA 3/VISTA ALPINA FRENTE A PISCINA.jpg",
            "PISCINA/NUESTRA PISCINA.jpg",
        ],
        "hero",
    ),
    (
        "01-complejo-panoramica",
        [
            "PARQUE/vista panoramica desde el complejo.jpg",
            "PARQUE/VISTA PANORAMICA INCREIBLE DESDE EL PARQUE.jpg",
            "CABAÑA ALPINA 3/VISTA ALPINA FRENTE A PISCINA.jpg",
        ],
        "complejo",
    ),
    ("02-piscina", ["PISCINA/NUESTRA PISCINA.jpg", "PISCINA/DIA HERMOSO PARA PISCINA.jpg"], "amenity"),
    (
        "03-pileta-alpina",
        [
            "CABAÑA ALPINA 3/VISTA ALPINA FRENTE A PISCINA.jpg",
            "PISCINA/REPOSERAS SOL Y PILE.jpg",
        ],
        "lifestyle",
    ),
    (
        "04-alpina-vista-puerta",
        ["CABANA ALPINA 1/VISTA PANORAMICA DESDE LA PUERTA DE LA CABAÑA.jpg"],
        "alpina",
    ),
    (
        "05-alpina-living",
        ["CABANA ALPINA 1/LIVING COMEDOR CABAÑA ALPINA CON 2 CAMAS DE 1 PLAZA.jpeg"],
        "alpina",
    ),
    (
        "06-suite5-ventanal",
        ["CABAÑA SUITE 5/HERMOSO VENTANAL CON VISTA A LAS SIERRAS DE CABAÑA SUITE PLANTA ALTA.jpg"],
        "suite-5",
    ),
    ("07-suite4-interior", ["CABAÑA SUITE 4/INTERIOR CABAÑA SUITE PB.jpg"], "suite-4"),
    ("08-suites-exterior", ["CABAÑA SUITE 4/VISTA EXTERIOR CABAÑA SUITE.jpg"], "suites"),
    (
        "09-alpina-frente-pileta",
        ["CABAÑA ALPINA 3/VISTA ALPINA FRENTE A PISCINA.jpg", "PISCINA/PARQUE Y PISCINA.jpg"],
        "alpina",
    ),
    ("10-parque-mate", ["CABAÑA ALPINA 2/PERGOLA CON ASADOR EN EL PARQUE.jpg"], "parque"),
    (
        "11-lago-plaza",
        [
            "RIO Y BALNEARIOS/vista del lago desde la plaza federal caminata a  1km del complejo.jpg",
        ],
        "entorno",
    ),
    (
        "12-arroyo-cercano",
        ["RIO Y BALNEARIOS/arroyo las mojarras cerquita del complejo.jpg"],
        "entorno",
    ),
    (
        "13-parque-relax",
        [
            "PISCINA/REPOSERAS SOL Y PILE.jpg",
            "exteriores cabanas/reposera pileta y alpina moe_edited.jpeg",
            "PISCINA/PARQUE Y PISCINA.jpg",
        ],
        "parque",
    ),
    (
        "14-pileta-relax",
        [
            "PISCINA/RELAX EN LA PISCINA.jpg",
            "PISCINA/TOMANDO SOL EN LA PILE.jpg",
        ],
        "pileta",
    ),
    (
        "15-pileta-frutillas",
        [
            "PISCINA/RELAX EN LA PISCINA.jpg",
            "PISCINA/TOMANDO SOL EN LA PILE.jpg",
            "PISCINA/PARQUE Y PISCINA.jpg",
        ],
        "pileta",
    ),
]

UNIT_IMAGES = {
    "alpina": "04-alpina-vista-puerta.jpg",
    "suite-4": "07-suite4-interior.jpg",
    "suite-5": "06-suite5-ventanal.jpg",
}

UNIT_SOURCE_DIRS: dict[str, list[str]] = {
    "alpina-1": ["CABANA ALPINA 1", "CABAÑA ALPINA 1"],
    "alpina-2": ["CABANA ALPINA 2", "CABAÑA ALPINA 2"],
    "alpina-3": ["CABANA ALPINA 3", "CABAÑA ALPINA 3"],
    "suite-4": ["CABANA SUITE 4", "CABAÑA SUITE 4"],
    "suite-5": ["CABANA SUITE 5", "CABAÑA SUITE 5"],
}

UNIT_OUT = REPO / "frontend" / "public" / "media" / "unidades"
MAX_UNIT_PHOTOS = 8
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}


def _resolve_unit_dir(uid: str) -> Path | None:
    for name in UNIT_SOURCE_DIRS.get(uid, []):
        p = SRC_ROOT / name
        if p.is_dir():
            return p
    return None


def _resolve_src(candidates: list[str]) -> Path | None:
    for rel in candidates:
        p = SRC_ROOT / rel
        if p.is_file():
            return p
    names = {Path(c).name.lower() for c in candidates}
    for p in SRC_ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXT and p.name.lower() in names:
            return p
    return None


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
        im.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=False)


def main() -> int:
    if not SRC_ROOT.is_dir():
        print(f"No existe carpeta origen: {SRC_ROOT}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_items: list[dict] = []
    missing: list[str] = []
    used_hashes: set[int] = set()

    for slug, candidates, rol in CURATED:
        src = _resolve_src(candidates)
        dest = OUT_DIR / f"{slug}.jpg"
        if src is None:
            missing.append(" | ".join(candidates[:2]))
            continue
        data = src.read_bytes()
        digest = hash(data)
        if digest in used_hashes and slug not in ("09-alpina-frente-pileta", "15-pileta-frutillas"):
            print(f"SKIP duplicado {slug} (mismo archivo que otro)")
            continue
        used_hashes.add(digest)
        _resize_save(src, dest)
        rel_used = str(src.relative_to(SRC_ROOT)).replace("\\", "/")
        manifest_items.append(
            {
                "id": slug,
                "archivo": f"media/galeria/{slug}.jpg",
                "rol": rol,
                "origen": rel_used,
            }
        )
        print(f"OK {slug} <- {rel_used}")

    json_path = REPO / "frontend" / "public" / "assets" / "data" / "galeria.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(
            {"version": 2, "items": manifest_items, "unidades": UNIT_IMAGES},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    unit_manifest: dict[str, list[str]] = {}
    for uid in UNIT_SOURCE_DIRS:
        src_dir = _resolve_unit_dir(uid)
        if src_dir is None:
            continue
        out_dir = UNIT_OUT / uid
        out_dir.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []
        files = sorted(
            p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXT
        )[:MAX_UNIT_PHOTOS]
        for i, src in enumerate(files, start=1):
            dest = out_dir / f"{i:02d}.jpg"
            _resize_save(src, dest)
            paths.append(f"media/unidades/{uid}/{dest.name}")
            print(f"OK unidad {uid} <- {src.name}")
        unit_manifest[uid] = paths

    unidades_json = REPO / "frontend" / "public" / "assets" / "data" / "unidades.json"
    if unidades_json.is_file() and any(unit_manifest.values()):
        data = json.loads(unidades_json.read_text(encoding="utf-8"))
        for u in data.get("unidades", []):
            fotos = unit_manifest.get(u.get("id") or "")
            if fotos:
                u["fotos"] = fotos
        unidades_json.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    if missing:
        print("FALTAN:", *missing, sep="\n  ")
        return 2
    print(f"Listo: {len(manifest_items)} imágenes en {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
