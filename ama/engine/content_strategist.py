"""
Genera copy para redes y WhatsApp desde plantillas YAML (sin API de pago obligatoria).
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import yaml

_TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "copy_prompts.yaml"


def _load_templates() -> dict:
    if not _TEMPLATES.is_file():
        return {}
    with _TEMPLATES.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def generar_copy(
    *,
    angulo: str = "parejas",
    canal: str = "instagram",
    tema_extra: str = "",
    cuerpo_extra: str | None = None,
) -> dict:
    tpl = _load_templates()
    angulos = tpl.get("angulos") or {}
    meta = angulos.get(angulo) or angulos.get("parejas") or {}
    titulo = meta.get("titulo", "Terra Natura — Bialet Massé")
    hashtags = list(meta.get("hashtags") or [])

    extras = (tpl.get("extras_por_tema") or {}).get(tema_extra, "")
    if cuerpo_extra is None:
        cuerpo_extra = extras or "Consultá disponibilidad para tu escapada en Punilla."

    wa = tpl.get("whatsapp_link") or "https://wa.me/5493541571190"
    cta_linea = wa
    hashtags_linea = " ".join(hashtags[:8])

    plantilla_canal = (tpl.get("cuerpos") or {}).get(canal) or (tpl.get("cuerpos") or {}).get("instagram", "{titulo}\n\n{cuerpo_extra}")
    copy = plantilla_canal.format(
        titulo=titulo,
        cuerpo_extra=cuerpo_extra,
        cta_linea=cta_linea,
        hashtags_linea=hashtags_linea,
    ).strip()

    wa_prefill = f"Hola! Vi su publicación sobre {angulo.replace('_', ' ')} en Terra Natura. Consulto disponibilidad..."
    wa_url = f"{wa}?text={quote(wa_prefill)}"

    return {
        "angulo": angulo,
        "canal": canal,
        "titulo": titulo,
        "copy": copy,
        "hashtags": hashtags,
        "whatsapp_url": wa_url,
        "brief_canva": f"Imagen: paisaje Punilla o {angulo}. Texto overlay: {titulo[:50]}. Logo Terra Natura.",
    }
