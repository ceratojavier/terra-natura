#!/usr/bin/env python3
"""
Renombra carpetas y archivos: quita caracteres españoles ñ/Ñ (y NFD ñ/Ñ) del NOMBRE.
Orden: rutas más profundas primero (archivos dentro de carpeta antes que la carpeta).

Uso (desde carpeta raíz del proyecto):
  python local/normalizar_nombres_sin_tilde.py
  python local/normalizar_nombres_sin_tilde.py "ruta/o/a/archivos multimedia"
  python local/normalizar_nombres_sin_tilde.py --dry-run

Sin argumentos procesa por defecto:
  Proyecto Terra Natura/archivos multimedia
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path


def nombre_sin_tilde(name: str) -> str:
    """Convierte ñ, Ñ y n+NFC tilde combinante → n/N."""
    s = name.replace("\u00f1", "n").replace("\u00d1", "N")
    norm = unicodedata.normalize("NFD", s)
    norm = re.sub(r"n\u0303", "n", norm)
    norm = re.sub(r"N\u0303", "N", norm)
    return unicodedata.normalize("NFC", norm)


def main() -> int:
    parser = argparse.ArgumentParser(description="Renombrar ñ→n en rutas locales")
    parser.add_argument(
        "directorio",
        nargs="?",
        default=None,
        help="Carpeta raíz (default: ../archivos multimedia junto al repo)",
    )
    parser.add_argument("--dry-run", action="store_true", help="No renombra; solo muestra cambios")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    proyecto = here.parent

    root = Path(args.directorio) if args.directorio else proyecto / "archivos multimedia"

    if not root.is_dir():
        print(f"ERROR: No existe carpeta: {root}", file=sys.stderr)
        return 1

    todos = sorted(root.rglob("*"), key=lambda p: len(str(p)), reverse=True)
    cambios = 0
    for p in todos:
        if not p.exists():
            continue
        nuevo = nombre_sin_tilde(p.name)
        if nuevo == p.name:
            continue
        destino = p.parent / nuevo
        if destino.exists():
            print(f"SALTAR (destino ocupado): {p.name} -> {nuevo}")
            continue
        print(f"{p.relative_to(root)} -> {nuevo}")
        if not args.dry_run:
            p.rename(destino)
        cambios += 1

    print(f"\nRenombrados: {cambios}" + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
