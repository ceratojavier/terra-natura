"""Importa fotos nuevas del chat y genera ambos videos (Belgrano + River)."""
from __future__ import annotations

from pathlib import Path

from ama.video.build_from_folder import build_from_folder
from ama.video.import_fotos_chat import import_all

BASE = Path(__file__).resolve().parent.parent / "output" / "assets"


def main() -> None:
    print("=== Importar fotos del chat ===")
    import_all()
    print("\n=== Video BELGRANO ===")
    build_from_folder(
        BASE / "propias",
        "belgrano",
        "kempes_belgrano_TUS_FOTOS_whatsapp.mp4",
        (6, 18, 14),
    )
    print("\n=== Video RIVER ===")
    build_from_folder(
        BASE / "propias_river",
        "river",
        "kempes_river_TUS_FOTOS_whatsapp.mp4",
        (22, 10, 12),
    )


if __name__ == "__main__":
    main()
