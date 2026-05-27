"""
Analiza MP4 de referencia (reels guardados) — duración, ritmo de cortes, preset sugerido.
No descarga Instagram; solo archivos locales en marketing/sistema/referencias_reels/videos/
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
REF_DIR = REPO / "marketing" / "sistema" / "referencias_reels"
VIDEOS = REF_DIR / "videos"
INDICE = REF_DIR / "indice.json"


def _ffmpeg() -> str:
    f = shutil.which("ffmpeg")
    if not f:
        raise RuntimeError("Instalá ffmpeg en el PATH.")
    return f


def probe_duration(path: Path) -> float:
    from ama.video.youtube_broll import _probe_duration

    return max(0.5, float(_probe_duration(path)))


def count_scene_cuts(path: Path, threshold: float = 0.28) -> int:
    """Estima cantidad de cambios de plano (scene detect)."""
    ff = _ffmpeg()
    cmd = [
        ff,
        "-i",
        str(path),
        "-filter:v",
        f"select='gt(scene,{threshold})',showinfo",
        "-f",
        "null",
        "-",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    text = (r.stderr or "") + (r.stdout or "")
    return len(re.findall(r"pts_time:", text))


def sugerir_preset(duracion: float, cortes: int) -> str:
    if duracion <= 0:
        return "clasico_cabana"
    promedio = duracion / max(1, cortes + 1)
    if promedio < 3.2:
        return "rapido_trend"
    if promedio > 4.5:
        return "lento_emocional"
    return "clasico_cabana"


def analizar_video(path: Path) -> dict:
    dur = probe_duration(path)
    cortes = count_scene_cuts(path)
    preset = sugerir_preset(dur, cortes)
    prom = dur / max(1, cortes + 1)
    return {
        "id": f"ref_{path.stem[:40]}",
        "archivo": str(path.relative_to(REPO)).replace("\\", "/"),
        "duracion_total_seg": round(dur, 1),
        "cantidad_cortes": cortes,
        "duracion_plano_promedio": round(prom, 2),
        "hook_seg": 2.0 if dur > 8 else 1.5,
        "preset_sugerido": preset,
        "analizado_en": datetime.now(timezone.utc).isoformat(),
        "notas": "Auto — completá gancho y cuenta en indice.json",
    }


def analizar_carpeta_videos() -> dict:
    VIDEOS.mkdir(parents=True, exist_ok=True)
    indice = {"meta": {}, "referencias": []}
    if INDICE.is_file():
        indice = json.loads(INDICE.read_text(encoding="utf-8"))

    nuevas = []
    for mp4 in sorted(VIDEOS.glob("*.mp4")):
        try:
            nuevas.append(analizar_video(mp4))
        except Exception as exc:
            nuevas.append({"archivo": mp4.name, "error": str(exc)})

    # merge por id/archivo
    prev = {r.get("archivo") or r.get("id"): r for r in indice.get("referencias", [])}
    for r in nuevas:
        if r.get("error"):
            continue
        key = r.get("archivo")
        prev[key] = {**prev.get(key, {}), **r}

    refs = list(prev.values())
    estilo_activo = indice.get("meta", {}).get("estilo_activo") or "clasico_cabana"
    if refs:
        # estilo más votado por preset sugerido
        from collections import Counter

        c = Counter(r.get("preset_sugerido", "clasico_cabana") for r in refs if "preset_sugerido" in r)
        estilo_activo = c.most_common(1)[0][0]

    indice["meta"] = {
        **(indice.get("meta") or {}),
        "ultima_actualizacion": datetime.now(timezone.utc).isoformat(),
        "estilo_activo": estilo_activo,
        "total_referencias": len(refs),
    }
    indice["referencias"] = refs
    REF_DIR.mkdir(parents=True, exist_ok=True)
    INDICE.write_text(json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "analizados": len(nuevas), "estilo_activo": estilo_activo, "indice": str(INDICE)}


def main() -> None:
    r = analizar_carpeta_videos()
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
