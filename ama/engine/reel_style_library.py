"""
Biblioteca de estilos de reel — presets + referencias analizadas (indice.json).
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PRESETS = Path(__file__).resolve().parent.parent / "data" / "reel_estilos_preset.json"
INDICE = REPO / "marketing" / "sistema" / "referencias_reels" / "indice.json"


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def estilo_activo_id() -> str:
    idx = _load_json(INDICE)
    return (idx.get("meta") or {}).get("estilo_activo") or _load_json(PRESETS).get("meta", {}).get(
        "default", "clasico_cabana"
    )


def get_estilo(estilo_id: str | None = None) -> dict:
    presets = _load_json(PRESETS)
    eid = estilo_id or estilo_activo_id()
    estilos = presets.get("estilos") or {}
    base = dict(estilos.get(eid) or estilos.get("clasico_cabana") or {})
    base["id"] = eid
    base["nombre"] = base.get("nombre", eid)

    idx = _load_json(INDICE)
    refs = idx.get("referencias") or []
    if refs and not estilo_id:
        # Promediar duraciones de referencias si hay
        durs = [r["duracion_plano_promedio"] for r in refs if r.get("duracion_plano_promedio")]
        if durs:
            base["duracion_plano_promedio"] = sum(durs) / len(durs)
        hooks = [r["hook_seg"] for r in refs if r.get("hook_seg")]
        if hooks:
            base["hook_seg"] = sum(hooks) / len(hooks)
    return base


def aplicar_duraciones_a_secuencia(secuencia: list[dict], estilo: dict) -> list[dict]:
    """Ajusta duracion_seg de cada paso según estilo (rapido/lento)."""
    prom = float(estilo.get("duracion_plano_promedio") or 3.8)
    out = []
    for step in secuencia:
        s = dict(step)
        t = s.get("tipo")
        if t == "hook_card":
            s["duracion_seg"] = float(estilo.get("hook_seg") or 2.2)
        elif t == "cierre":
            s["duracion_seg"] = max(3.5, prom)
        elif t in ("broll_youtube", "foto", "clip_youtube"):
            s["duracion_seg"] = prom
        out.append(s)
    return out


def hook_plantilla(estilo: dict, objetivo: str) -> str | None:
    h = estilo.get("hook_plantilla")
    if h:
        return str(h)
    return None
