"""Descarga fotos REALES (Wikimedia CC) — hinchada Belgrano, Kempes, estadio."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "output" / "assets"
UA = "TerraNatura-Marketing/1.0 (uso local; sin redistribución comercial)"

# Título Commons → nombre local
FILES = {
    "kempes_aereo.jpg": "File:Vista aérea del Estadio Mario Alberto Kempes, Córdoba.jpg",
    "kempes_ingreso.jpg": "File:Ingreso Estadio Kempes. Córdoba, Argentina.jpg",
    "kempes_post_partido.jpg": "File:Estadio Kempes luego de finalizar un partido.jpg",
    "la14_presente.jpg": "File:La 14 presente.jpg",
    "la14_fiesta.jpg": "File:La 14 de fiesta.jpg",
    "belgrano_bandera.png": "File:Bandera del Club Atlético Belgrano de Córdoba.png",
    "belgrano_partido.jpg": "File:Belgrano vs San Miguel 2022 23.jpg",
    "belgrano_estadio_2025.jpg": "File:Estadio del Club Atlético Belgrano 2025 GP3.jpg",
}


def _commons_url(title: str) -> tuple[str, str]:
    u = (
        "https://commons.wikimedia.org/w/api.php?action=query&titles="
        + urllib.parse.quote(title)
        + "&prop=imageinfo&iiprop=url|extmetadata&format=json"
    )
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    data = json.load(urllib.request.urlopen(req, timeout=90))
    page = next(iter(data["query"]["pages"].values()))
    ii = page["imageinfo"][0]
    lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?")
    return ii["url"], lic


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    credits = []
    for local, title in FILES.items():
        dest = ASSETS / local
        if dest.is_file() and dest.stat().st_size > 5000:
            print("skip", local)
            continue
        time.sleep(2.5)
        url, lic = _commons_url(title)
        time.sleep(1.0)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        dest.write_bytes(urllib.request.urlopen(req, timeout=120).read())
        credits.append(f"{local}\n  Fuente: {title}\n  URL: {url}\n  Licencia: {lic}\n")
        print("OK", local)
    (ASSETS.parent / "videos" / "CREDITOS_IMAGENES.txt").parent.mkdir(parents=True, exist_ok=True)
    out = ASSETS.parent / "videos" / "CREDITOS_IMAGENES.txt"
    out.write_text(
        "Imágenes de fútbol — Wikimedia Commons (uso con atribución).\n"
        "La 14 = hinchada oficial del Club Atlético Belgrano (Córdoba).\n\n"
        + "\n".join(credits),
        encoding="utf-8",
    )
    print("Créditos:", out)


if __name__ == "__main__":
    main()
