"""Belgrano: importa fotos del chat + video con movimiento (todas las de propias/)."""
from __future__ import annotations

from pathlib import Path

from ama.video.build_from_folder import build_from_folder
from ama.video.import_fotos_chat import import_all

BASE = Path(__file__).resolve().parent.parent / "output" / "assets"


def build() -> Path:
    import_all()
    return build_from_folder(
        BASE / "propias",
        "belgrano",
        "kempes_belgrano_TUS_FOTOS_whatsapp.mp4",
        (6, 18, 14),
    )


if __name__ == "__main__":
    build()
