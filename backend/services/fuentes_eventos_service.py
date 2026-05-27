"""
Configuración de fuentes de agenda — catálogo + preferencias del configurador.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent.parent
_CATALOGO = _REPO / "ama" / "data" / "fuentes_agenda_eventos.json"
_CONFIG_WIZARD = _REPO / "marketing" / "contexto" / "fuentes_eventos_config.json"

_SECCIONES: list[tuple[str, str, str]] = [
    ("datos_proyecto", "datos_internos", "Datos del proyecto (automático)"),
    ("oficial", "fuentes_oficiales", "Oficiales"),
    ("local", "fuentes_locales", "Local Bialet / Punilla"),
    ("medios", "medios_regionales", "Medios y agenda regional"),
    ("deportes", "deportes", "Deportes (running, ciclismo, rally…)"),
    ("musica", "musica_recitales", "Música y recitales (Kempes, Cosquín…)"),
]

# IDs con scraper o JSON activo hoy
_SCRAPERS_ACTIVOS = frozenset(
    {
        "cordoba_turismo",
        "confirmados_manuales",
        "calendario_importante",
        "fiestas_recurrentes",
        "turismo_seed",
        "feriados_argentina",
    }
)


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _flatten_catalogo() -> list[dict[str, Any]]:
    raw = _load_json(_CATALOGO)
    out: list[dict[str, Any]] = []
    for sec_id, key, titulo in _SECCIONES:
        for row in raw.get(key) or []:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            fid = str(row["id"])
            estado = row.get("estado_scraper") or (
                "activo" if fid in _SCRAPERS_ACTIVOS else "referencia"
            )
            out.append(
                {
                    **row,
                    "id": fid,
                    "seccion": sec_id,
                    "seccion_titulo": titulo,
                    "estado_scraper": estado,
                    "habilitada_default": row.get("habilitada_default", True),
                }
            )
    return out


def catalogo_ui() -> list[dict[str, Any]]:
    """Catálogo agrupado para el configurador."""
    flat = _flatten_catalogo()
    grupos: dict[str, dict[str, Any]] = {}
    for row in flat:
        g = grupos.setdefault(
            row["seccion"],
            {"id": row["seccion"], "titulo": row["seccion_titulo"], "fuentes": []},
        )
        g["fuentes"].append(row)
    orden = [s[0] for s in _SECCIONES]
    return [grupos[k] for k in orden if k in grupos]


def _defaults_habilitadas() -> dict[str, bool]:
    return {r["id"]: bool(r.get("habilitada_default", True)) for r in _flatten_catalogo()}


def normalize_eventos(valores: dict[str, Any] | None) -> dict[str, Any]:
    v = dict(valores or {})
    hab = dict(_defaults_habilitadas())
    hab.update({k: bool(vv) for k, vv in (v.get("habilitadas") or {}).items()})
    custom = []
    for row in v.get("fuentes_personalizadas") or []:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or "").strip()
        nombre = str(row.get("nombre") or "").strip()
        if not nombre and not url:
            continue
        custom.append(
            {
                "id": str(row.get("id") or f"custom-{len(custom)+1}"),
                "nombre": nombre or "Fuente personalizada",
                "url": url,
                "categoria": str(row.get("categoria") or "otro").strip() or "otro",
                "habilitada": bool(row.get("habilitada", True)),
                "notas": str(row.get("notas") or "")[:300],
                "estado_scraper": "personalizada",
            }
        )
    v["habilitadas"] = hab
    v["fuentes_personalizadas"] = custom
    return v


def guardar_runtime_config(valores: dict[str, Any]) -> None:
    v = normalize_eventos(valores)
    ctx = _CONFIG_WIZARD.parent
    ctx.mkdir(parents=True, exist_ok=True)
    payload = {
        "habilitadas": v["habilitadas"],
        "fuentes_personalizadas": v["fuentes_personalizadas"],
        "catalogo_version": (_load_json(_CATALOGO).get("meta") or {}).get("version", 1),
    }
    _CONFIG_WIZARD.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def cargar_runtime_config() -> dict[str, Any]:
    """Preferencias para event_hunter (configurador o defaults)."""
    if _CONFIG_WIZARD.is_file():
        try:
            raw = _load_json(_CONFIG_WIZARD)
            return normalize_eventos(
                {
                    "habilitadas": raw.get("habilitadas"),
                    "fuentes_personalizadas": raw.get("fuentes_personalizadas"),
                }
            )
        except Exception:
            pass
    try:
        cfg_path = _REPO / "local" / "config-dueño.json"
        if cfg_path.is_file():
            raw = json.loads(cfg_path.read_text(encoding="utf-8"))
            ev = raw.get("datos", {}).get("eventos")
            if ev:
                return normalize_eventos(ev)
    except Exception:
        pass
    return normalize_eventos({})


def fuente_habilitada(cfg: dict[str, Any], fuente_id: str) -> bool:
    return bool((cfg.get("habilitadas") or {}).get(fuente_id, True))


def catalogo_por_id() -> dict[str, dict[str, Any]]:
    return {r["id"]: r for r in _flatten_catalogo()}


def _texto_evento(ev: dict) -> str:
    tags = ev.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    parts = [
        str(ev.get("nombre") or ""),
        str(ev.get("localidad") or ""),
        str(ev.get("categoria") or ""),
        " ".join(str(t) for t in tags),
        str(ev.get("descripcion") or "")[:200],
    ]
    return " ".join(parts).lower()


def evento_coincide_fuente(ev: dict, fuente: dict) -> bool:
    cubre = fuente.get("cubre") or []
    if not cubre:
        return False
    texto = _texto_evento(ev)
    for token in cubre:
        t = str(token).lower().replace("_", " ")
        if t in texto:
            return True
        if re.search(re.escape(t), texto):
            return True
    return False


def evento_permitido_por_fuentes(ev: dict, cfg: dict[str, Any]) -> bool:
    """Filtra eventos de JSON local según fuentes habilitadas."""
    if fuente_habilitada(cfg, "calendario_importante"):
        return True
    cat = catalogo_por_id()
    for fid, on in (cfg.get("habilitadas") or {}).items():
        if not on or fid in ("calendario_importante", "confirmados_manuales"):
            continue
        fuente = cat.get(fid)
        if fuente and evento_coincide_fuente(ev, fuente):
            return True
    for custom in cfg.get("fuentes_personalizadas") or []:
        if not custom.get("habilitada"):
            continue
        if evento_coincide_fuente(ev, custom):
            return True
    return False


def check_eventos(d: dict[str, Any]) -> dict[str, Any]:
    cfg = normalize_eventos(d)
    hab = cfg.get("habilitadas") or {}
    n_on = sum(1 for v in hab.values() if v)
    n_custom = sum(1 for c in cfg.get("fuentes_personalizadas") or [] if c.get("habilitada"))
    activos = [fid for fid in _SCRAPERS_ACTIVOS if fuente_habilitada(cfg, fid)]

    cache_path = _REPO / "ama" / "data" / "eventos_agenda_cache.json"
    ultima = None
    if cache_path.is_file():
        try:
            ultima = _load_json(cache_path).get("actualizado_en", "")[:16]
        except Exception:
            pass

    ok = n_on >= 2 and len(activos) >= 1
    msg = f"{n_on} fuentes activas"
    if n_custom:
        msg += f" + {n_custom} personalizada(s)"
    if activos:
        msg += f" · scrapers: {', '.join(activos[:4])}"
        if len(activos) > 4:
            msg += "…"
    if ultima:
        msg += f" · última sync {ultima}"
    return {
        "estado": "ok" if ok and ultima else "parcial" if n_on else "pendiente",
        "mensaje": msg,
        "detalle": {"habilitadas": n_on, "scrapers": activos, "ultima_sync": ultima},
    }


def resumen_para_ui() -> dict[str, Any]:
    cfg = cargar_runtime_config()
    return {
        "grupos": catalogo_ui(),
        "valores": cfg,
        "scrapers_activos": sorted(_SCRAPERS_ACTIVOS),
    }
