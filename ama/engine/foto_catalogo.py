"""
Catálogo de fotos locales — selección y auditoría de calidad para guiones de producción.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent.parent
_MEDIA = _REPO / "archivos multimedia"
_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# Palabras clave de escena → subcarpetas bajo archivos multimedia/
_CARPETAS_POR_TEMA: dict[str, list[str]] = {
    "lago": ["RIO Y BALNEARIOS", "exteriores cabanas", "fotos terra natura/exteriores cabanas"],
    "rio": ["RIO Y BALNEARIOS", "fotos terra natura/RIO Y BALNEARIOS"],
    "sierras": ["exteriores cabanas", "fotos terra natura/exteriores cabanas", "PARQUE"],
    "bialet": ["exteriores cabanas", "PARQUE", "fotos terra natura/PARQUE"],
    "parque": ["PARQUE", "PISCINA", "fotos terra natura/PARQUE", "fotos terra natura/PISCINA"],
    "pileta": ["PISCINA", "fotos terra natura/PISCINA"],
    "alpina": ["CABANA ALPINA 1", "CABANA ALPINA 2", "CABANA ALPINA 3"],
    "suite": ["CABANA SUITE 4", "CABANA SUITE 5"],
    "interior": [
        "CABANA ALPINA 1",
        "CABANA ALPINA 2",
        "CABANA ALPINA 3",
        "CABANA SUITE 4",
        "CABANA SUITE 5",
    ],
    "matrimonial": ["CABANA ALPINA 1", "CABANA SUITE 5"],
    "atardecer": ["exteriores cabanas", "PARQUE", "PISCINA"],
    "marca": ["LOGO", "recursos de la marca", "fotos terra natura/LOGO"],
}


def _rel(path: Path) -> str:
    return str(path.relative_to(_REPO)).replace("\\", "/")


def auditar_imagen(ruta_rel: str) -> dict[str, Any]:
    """Dimensiones y si alcanza para reel vertical."""
    p = _REPO / ruta_rel.replace("\\", "/")
    if not p.is_file():
        return {
            "ok": False,
            "nivel": "error",
            "mensaje": "Archivo no encontrado en el proyecto.",
            "ancho": 0,
            "alto": 0,
        }
    ancho, alto = 0, 0
    try:
        from PIL import Image

        with Image.open(p) as im:
            ancho, alto = im.size
    except Exception:
        size_kb = p.stat().st_size / 1024
        if size_kb < 80:
            return {
                "ok": False,
                "nivel": "bajo",
                "mensaje": "Archivo muy liviano; puede verse pixelado en pantalla.",
                "ancho": 0,
                "alto": 0,
            }
        return {
            "ok": True,
            "nivel": "ok",
            "mensaje": "Tamaño de archivo aceptable (sin leer dimensiones).",
            "ancho": 0,
            "alto": 0,
        }

    corto = min(ancho, alto)
    if corto < 720:
        return {
            "ok": False,
            "nivel": "bajo",
            "mensaje": f"Resolución baja ({ancho}×{alto}). Buscá otra foto o exportá más grande.",
            "ancho": ancho,
            "alto": alto,
        }
    if corto < 1080:
        return {
            "ok": True,
            "nivel": "advertencia",
            "mensaje": f"Usable ({ancho}×{alto}), pero ideal ≥1080 px en el lado corto.",
            "ancho": ancho,
            "alto": alto,
        }
    return {
        "ok": True,
        "nivel": "ok",
        "mensaje": f"Calidad correcta para reel ({ancho}×{alto}).",
        "ancho": ancho,
        "alto": alto,
    }


def _score_nombre(path: Path, keywords: list[str]) -> int:
    blob = f"{path.parent.name} {path.name}".lower()
    score = 0
    for kw in keywords:
        k = kw.lower()
        if k in blob:
            score += 3
        for part in re.split(r"[\s_\-]+", k):
            if len(part) > 2 and part in blob:
                score += 1
    return score


def listar_candidatas(
    *,
    temas: list[str] | None = None,
    keywords: list[str] | None = None,
    max_scan: int = 120,
) -> list[Path]:
    carpetas: list[Path] = []
    for t in temas or []:
        for rel in _CARPETAS_POR_TEMA.get(t, []):
            base = _MEDIA / rel.replace("\\", "/")
            if base.is_dir():
                carpetas.append(base)
    if not carpetas:
        carpetas = [_MEDIA / "fotos terra natura"] if (_MEDIA / "fotos terra natura").is_dir() else [_MEDIA]

    vistos: set[str] = set()
    out: list[Path] = []
    for base in carpetas:
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.suffix.lower() not in _EXTS or not p.is_file():
                continue
            key = str(p.resolve())
            if key in vistos:
                continue
            vistos.add(key)
            out.append(p)
            if len(out) >= max_scan:
                return out
    if keywords:
        out.sort(key=lambda x: _score_nombre(x, keywords), reverse=True)
    return out


def seleccionar_foto(
    *,
    temas: list[str] | None = None,
    keywords: list[str] | None = None,
    excluir: set[str] | None = None,
) -> dict[str, Any]:
    excluir = excluir or set()
    kws = list(keywords or []) + list(temas or [])
    candidatas = listar_candidatas(temas=temas, keywords=kws)
    mejor: Path | None = None
    mejor_score = -1
    for p in candidatas:
        rel = _rel(p)
        if rel in excluir:
            continue
        sc = _score_nombre(p, kws)
        audit = auditar_imagen(rel)
        if not audit.get("ok") and audit.get("nivel") == "error":
            continue
        bonus = 2 if audit.get("nivel") == "ok" else 0
        total = sc + bonus
        if total > mejor_score:
            mejor_score = total
            mejor = p
    if not mejor:
        return {
            "ruta": "",
            "justificacion": "No hay foto en archivos multimedia/ para este tema. Subí material en la carpeta sugerida.",
            "calidad": {"ok": False, "nivel": "error", "mensaje": "Sin foto"},
            "carpetas_sugeridas": temas or ["PARQUE", "exteriores cabanas"],
        }
    rel = _rel(mejor)
    audit = auditar_imagen(rel)
    carpetas = []
    for t in temas or []:
        carpetas.extend(_CARPETAS_POR_TEMA.get(t, [])[:2])
    return {
        "ruta": rel,
        "nombre_archivo": mejor.name,
        "justificacion": (
            f"Elegida por coincidencia con la escena ({', '.join(kws[:4]) or 'tema general'}) "
            f"y carpeta «{mejor.parent.name}»."
        ),
        "calidad": audit,
        "carpetas_sugeridas": carpetas or ["fotos terra natura/PARQUE"],
    }
