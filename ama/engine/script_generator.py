"""
Guiones para reels — B-roll YouTube (biblioteca) + fotos Terra Natura + marca.
"""
from __future__ import annotations

from typing import Any

from ama.engine.broll_queries import BROLL_POR_TIPO, SECUENCIA_POR_OBJETIVO


def generar_guion(
    *,
    objetivo: str,
    canal: str,
    formato: str,
    angulo: str,
    titulo: str,
    evento: dict | None = None,
    assets: dict | None = None,
    estilo_reel: str | None = None,
) -> dict:
    from ama.engine.reel_style_library import aplicar_duraciones_a_secuencia, get_estilo, hook_plantilla

    assets = assets or {}
    fotos = assets.get("fotos") or []
    yt_clips = assets.get("youtube_clips") or []
    hook_evento = (evento or {}).get("copy_hook") or (evento or {}).get("mensaje_campana") or ""

    estilo = get_estilo(estilo_reel or assets.get("estilo_reel"))
    seq_key = estilo.get("secuencia_objetivo") or objetivo
    secuencia = SECUENCIA_POR_OBJETIVO.get(seq_key, SECUENCIA_POR_OBJETIVO.get(objetivo, SECUENCIA_POR_OBJETIVO["branding"]))
    secuencia = aplicar_duraciones_a_secuencia(secuencia, estilo)

    hooks = {
        "cta_reserva": "¿Listo para una escapada a las sierras?",
        "fidelizacion": "Hay lugares que te esperan de vuelta. Este es uno.",
        "utilidad": "Un finde en Bialet puede cambiar tu semana.",
        "branding": "Así se siente Terra Natura al atardecer.",
    }
    hook = hook_evento or hook_plantilla(estilo, objetivo) or hooks.get(objetivo, hooks["branding"])
    emotion_lines = _lineas_emocion(objetivo, angulo, evento)

    escenas: list[dict] = [
        {
            "tipo": "hook_card",
            "duracion_seg": float(estilo.get("hook_seg") or 2.2),
            "lineas": _lineas_hook(hook),
        },
    ]

    broll_idx = 0
    for step in secuencia:
        if step["tipo"] == "broll_youtube":
            broll_tipo = step.get("broll_tipo", "bialet")
            query = BROLL_POR_TIPO.get(broll_tipo, BROLL_POR_TIPO["bialet"])
            clip = yt_clips[broll_idx % len(yt_clips)] if yt_clips else {}
            broll_idx += 1
            escenas.append(
                {
                    "tipo": "broll_youtube",
                    "broll_tipo": broll_tipo,
                    "broll_query": query,
                    "youtube_id": clip.get("youtube_id"),
                    "fuente": clip.get("url"),
                    "duracion_seg": step.get("duracion_seg", 4.0),
                    "lineas": emotion_lines[len(escenas) % len(emotion_lines)],
                    "texto_pantalla": " ".join(emotion_lines[len(escenas) % len(emotion_lines)]),
                }
            )
        elif step["tipo"] == "foto":
            slot = step.get("slot", 0)
            foto = fotos[slot] if slot < len(fotos) else (fotos[0] if fotos else "")
            escenas.append(
                {
                    "tipo": "foto",
                    "fuente": foto,
                    "duracion_seg": step.get("duracion_seg", 3.6),
                    "lineas": emotion_lines[len(escenas) % len(emotion_lines)],
                    "effect": step.get("effect", "zoom_in"),
                    "transicion": "fade",
                }
            )
        elif step["tipo"] == "cierre":
            escenas.append(
                {
                    "tipo": "cierre",
                    "duracion_seg": step.get("duracion_seg", 4.0),
                    "lineas": ["Terra Natura", "Bialet Massé · Córdoba", "Reservá por WhatsApp"],
                    "cta": "wa.me/5493541571190",
                }
            )

    t = sum(e.get("duracion_seg", 3) for e in escenas)
    voz = _voz_off(objetivo, angulo, hook, evento)

    return {
        "objetivo": objetivo,
        "canal": canal,
        "formato": formato,
        "duracion_total_seg": round(t, 1),
        "hook": hook,
        "voz_off": voz,
        "musica": "instrumental cálida — ama/assets/music/musica_fondo.mp3",
        "escenas": escenas,
        "usa_biblioteca_youtube": True,
        "subtitulos": True,
        "estilo_video": "cinematico_broll_fotos",
        "estilo_reel": estilo.get("id"),
        "xfade_seg": estilo.get("xfade_seg", 0.45),
        "checklist_pre_publicar": [
            "B-roll de YouTube + fotos propias del complejo",
            "Revisar que el fragmento YouTube sea paisaje/entorno (no logo ajeno)",
            "Música de fondo y subtítulos",
        ],
    }


def _lineas_hook(hook: str) -> list[str]:
    words = hook.split()
    if len(words) <= 5:
        return [hook]
    mid = max(1, len(words) // 2)
    return [" ".join(words[:mid]), " ".join(words[mid:])]


def _lineas_emocion(objetivo: str, angulo: str, evento: dict | None) -> list[list[str]]:
    if evento and evento.get("tipo") == "finde_largo":
        return [
            ["El valle", "te espera"],
            ["Tu refugio", "en Punilla"],
            ["Agua y montaña", "cerca tuyo"],
            ["Reservá", "tu escapada"],
        ]
    if objetivo == "cta_reserva":
        return [
            ["Desconectá", "en Punilla"],
            ["600 m del lago", "Bialet Massé"],
            ["Tu cabaña", "con vista al valle"],
            ["Escribinos", "por WhatsApp"],
        ]
    if objetivo == "fidelizacion":
        return [
            ["Volver acá", "es volver a casa"],
            ["Gracias por", "elegirnos"],
            ["Naturaleza", "y tranquilidad"],
            ["Te esperamos", "de nuevo"],
        ]
    if objetivo == "utilidad":
        return [
            ["Río y sierras", "a minutos"],
            ["Bialet Massé", "te sorprende"],
            ["Finde corto", "gran cambio"],
            ["Guardá", "este lugar"],
        ]
    return [
        ["Terra Natura", "Valle de Punilla"],
        ["Amanecer", "en el parque"],
        ["Escapada", "real"],
        ["Bialet Massé", "Córdoba"],
    ]


def _voz_off(objetivo: str, angulo: str, hook: str, evento: dict | None) -> str:
    ev = ""
    if evento and evento.get("nombre"):
        ev = f" Este finde largo es ideal por {evento['nombre']}."
    if objetivo == "cta_reserva":
        return (
            f"{hook}{ev} "
            "Imaginá el río, el lago y después tu cabaña con vista al valle. "
            "En Terra Natura los dueños estamos en el predio. Escribinos por WhatsApp."
        )
    if objetivo == "fidelizacion":
        return (
            f"{hook} "
            "Si ya nos visitaste, conocés esta calma. Guardá el video y volvé cuando puedas."
        )
    if objetivo == "utilidad":
        return (
            f"{hook} "
            "Desde Bialet tenés naturaleza, río y paseos únicos. Compartilo con quien te debe una escapada."
        )
    return (
        f"{hook} "
        "Alpinas, suites, pileta y parque. Bialet Massé es tu base en Punilla."
    )
