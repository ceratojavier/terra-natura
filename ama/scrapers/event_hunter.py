"""
El Sabueso — actualiza agenda de eventos para un rango [desde, hasta].
Combina JSON locales, seed turismo, feriados y (cuando hay red) lectura liviana de fuentes públicas.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"
_CACHE = _DATA / "eventos_agenda_cache.json"
_FIESTAS = _DATA / "fiestas_recurrentes_extendido.json"
_CONFIRMADOS = _DATA / "eventos_confirmados_ar.json"
_FUENTES = _DATA / "fuentes_agenda_eventos.json"
_FERIADOS = _DATA / "feriados_puentes_ar.json"


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _mes_en_rango(mes: int, desde: date, hasta: date, anio: int) -> bool:
    ref_ini = date(anio, mes, 1)
    ref_fin = date(anio, mes, 28)
    return not (ref_fin < desde or ref_ini > hasta)


def _expandir_recurrente(ev: dict, desde: date, hasta: date) -> list[dict]:
    from ama.engine.evento_fechas import fechas_para_calendario

    out = []
    for anio in range(desde.year, hasta.year + 1):
        norm = fechas_para_calendario(ev, anio)
        if not norm:
            continue
        fi_s, ff_s = norm.get("fecha_inicio"), norm.get("fecha_fin")
        if fi_s:
            try:
                fi = date.fromisoformat(fi_s[:10])
                ff = date.fromisoformat((ff_s or fi_s)[:10])
            except ValueError:
                continue
            if ff < desde or fi > hasta:
                if not norm.get("solo_listado"):
                    continue
            else:
                norm.setdefault("fuente", ev.get("fuente", "fiestas_recurrentes_extendido.json"))
                out.append(norm)
                continue
        if norm.get("solo_listado"):
            norm.setdefault("fuente", ev.get("fuente", "fiestas_recurrentes_extendido.json"))
            norm.setdefault("tipo", "referencia")
            out.append(norm)
    return out


def _eventos_desde_seed_turismo(desde: date, hasta: date) -> list[dict]:
    try:
        from backend.services import turismo_seed_data as seed
    except ImportError:
        return []
    out = []
    for row in seed.EVENTOS:
        data = dict(row)
        fi = data.get("fecha_inicio")
        ff = data.get("fecha_fin")
        if isinstance(fi, str):
            fi = date.fromisoformat(fi[:10])
        if isinstance(ff, str):
            ff = date.fromisoformat(ff[:10])
        if fi and fi <= hasta and (ff or fi) >= desde:
            out.append(
                {
                    "nombre": data["nombre"],
                    "localidad": data.get("localidad"),
                    "categoria": data.get("categoria"),
                    "fecha_inicio": fi.isoformat(),
                    "fecha_fin": (ff or fi).isoformat(),
                    "descripcion": (data.get("descripcion") or "")[:300],
                    "tags": (data.get("tags") or "").split(",") if isinstance(data.get("tags"), str) else data.get("tags"),
                    "fuente": "turismo_seed_data.py",
                    "fuente_url": data.get("fuente_url"),
                    "prioridad": data.get("prioridad", 3),
                }
            )
        elif data.get("mes_inicio"):
            out.extend(_expandir_recurrente({**data, "fuente": "turismo_seed_data.py"}, desde, hasta))
    return out


def _recolectar_cordoba_turismo(desde: date, hasta: date) -> dict[str, Any]:
    """API oficial Tribe + sync local; filtra potencial estadía Bialet."""
    from ama.scrapers.sources_cordoba_turismo import recolectar_eventos_cordoba_turismo

    return recolectar_eventos_cordoba_turismo(desde=desde, hasta=hasta)


def _merge_feriados(hoy: date, hasta: date, merge) -> int:
    raw = _load(_FERIADOS)
    n = 0
    for f in raw.get("feriados_nacionales") or []:
        fi = f.get("fecha")
        if not fi:
            continue
        try:
            d = date.fromisoformat(fi[:10])
        except ValueError:
            continue
        if d < hoy or d > hasta:
            continue
        merge(
            {
                "nombre": f.get("nombre", "Feriado"),
                "fecha_inicio": d.isoformat(),
                "fecha_fin": d.isoformat(),
                "categoria": "feriado",
                "tipo": "feriado",
                "estado": "confirmado",
                "fuente": "feriados_puentes_ar.json",
                "prioridad": 2,
            }
        )
        n += 1
    for p in raw.get("fines_de_semana_largo") or []:
        fi, ff = p.get("fecha_inicio"), p.get("fecha_fin")
        if not fi:
            continue
        try:
            d_ini = date.fromisoformat(fi[:10])
            d_fin = date.fromisoformat((ff or fi)[:10])
        except ValueError:
            continue
        if d_fin < hoy or d_ini > hasta:
            continue
        merge(
            {
                "nombre": p.get("nombre", "Finde largo"),
                "fecha_inicio": d_ini.isoformat(),
                "fecha_fin": d_fin.isoformat(),
                "categoria": "puente",
                "tipo": p.get("tipo") or "finde_largo",
                "estado": "confirmado",
                "descripcion": p.get("copy_hook"),
                "copy_hook": p.get("copy_hook"),
                "angulo_comercial": p.get("copy_hook"),
                "audiencias": p.get("audiencias"),
                "noches_sugeridas": p.get("noches_sugeridas"),
                "fuente": "feriados_puentes_ar.json",
                "prioridad": 1,
                "masivo": True,
            }
        )
        n += 1
    return n


def actualizar_agenda(
    *,
    desde: date | None = None,
    hasta: date | None = None,
    db: Any | None = None,
    scrape_web: bool = True,
    fuentes_cfg: dict[str, Any] | None = None,
) -> dict:
    """
    Recolecta y fusiona eventos para el rango pedido. Guarda cache JSON auditable.
    """
    from backend.services.fuentes_eventos_service import (
        cargar_runtime_config,
        evento_permitido_por_fuentes,
        fuente_habilitada,
    )

    hoy = desde or date.today()
    if hasta is None:
        anio_marzo = hoy.year + 1 if hoy.month > 3 else hoy.year
        hasta = date(anio_marzo, 3, 31)

    cfg = fuentes_cfg or cargar_runtime_config()
    fuentes_usadas: list[str] = []

    items: list[dict] = []
    vistos: set[str] = set()

    def merge(nuevo: dict) -> None:
        key = f"{nuevo.get('nombre','')}|{nuevo.get('fecha_inicio')}|{nuevo.get('localidad')}"
        if key in vistos:
            return
        vistos.add(key)
        items.append(nuevo)

    if fuente_habilitada(cfg, "confirmados_manuales"):
        fuentes_usadas.append("confirmados_manuales")
    for ev in (
        _load(_CONFIRMADOS).get("eventos", [])
        if fuente_habilitada(cfg, "confirmados_manuales")
        else []
    ):
        fi = ev.get("fecha_inicio")
        ff = ev.get("fecha_fin") or fi
        if not fi:
            continue
        try:
            d_ini = date.fromisoformat(fi[:10])
            d_fin = date.fromisoformat((ff or fi)[:10])
        except ValueError:
            continue
        if d_fin < hoy or d_ini > hasta:
            continue
        merge(
            {
                **ev,
                "tipo": "evento_confirmado",
                "mostrar_en_calendario": True,
                "estado": "confirmado",
                "fuente": ev.get("fuente", "eventos_confirmados_ar.json"),
            }
        )

    imp_path = _DATA / "calendario_importante_ar.json"
    imp = _load(imp_path)
    calendario_on = fuente_habilitada(cfg, "calendario_importante") or any(
        fuente_habilitada(cfg, fid)
        for fid in (cfg.get("habilitadas") or {})
        if fid
        not in (
            "calendario_importante",
            "confirmados_manuales",
            "cordoba_turismo",
            "fiestas_recurrentes",
            "turismo_seed",
            "feriados_argentina",
        )
    )
    if calendario_on:
        fuentes_usadas.append("calendario_importante")
    for ev in (
        (imp.get("eventos_masivos", []) + imp.get("eventos_locales_bialet", []))
        if calendario_on
        else []
    ):
        estado = (ev.get("estado") or "").lower()
        if estado not in (
            "confirmado",
            "confirmado_pasado",
            "estimado_anual",
            "a_confirmar",
            "estimado",
        ):
            continue
        if not evento_permitido_por_fuentes(ev, cfg):
            continue
        fi = ev.get("fecha_inicio")
        ff = ev.get("fecha_fin") or fi
        if not fi:
            continue
        try:
            d_ini = date.fromisoformat(fi[:10])
            d_fin = date.fromisoformat((ff or fi)[:10])
        except ValueError:
            continue
        if d_fin < hoy or d_ini > hasta:
            continue
        merge(
            {
                "nombre": ev["nombre"],
                "localidad": ev.get("localidad"),
                "categoria": ev.get("categoria"),
                "fecha_inicio": d_ini.isoformat(),
                "fecha_fin": d_fin.isoformat(),
                "descripcion": ev.get("descripcion"),
                "tags": ev.get("tags"),
                "masivo": ev.get("masivo"),
                "prioridad": ev.get("prioridad", 2),
                "estado": ev.get("estado", "confirmado"),
                "fuente": "calendario_importante_ar.json",
            }
        )

    if db is not None:
        try:
            from backend.models.turismo import TurismoEvento

            for ev in db.query(TurismoEvento).filter(TurismoEvento.activo.is_(True)).all():
                if ev.fecha_inicio and ev.fecha_inicio <= hasta and (ev.fecha_fin or ev.fecha_inicio) >= hoy:
                    merge(
                        {
                            "nombre": ev.nombre,
                            "localidad": ev.localidad,
                            "categoria": ev.categoria,
                            "fecha_inicio": ev.fecha_inicio.isoformat(),
                            "fecha_fin": (ev.fecha_fin or ev.fecha_inicio).isoformat(),
                            "descripcion": (ev.descripcion or "")[:300],
                            "fuente": "turismo_eventos (BD)",
                            "prioridad": ev.prioridad,
                        }
                    )
                elif ev.mes_inicio:
                    for x in _expandir_recurrente(
                        {
                            "nombre": ev.nombre,
                            "localidad": ev.localidad,
                            "categoria": ev.categoria,
                            "mes_inicio": ev.mes_inicio,
                            "mes_fin": ev.mes_fin,
                            "dia_aprox": ev.dia_aprox,
                            "descripcion": ev.descripcion,
                            "prioridad": ev.prioridad,
                        },
                        hoy,
                        hasta,
                    ):
                        x["fuente"] = "turismo_eventos (BD, mes)"
                        merge(x)
        except Exception:
            pass

    if fuente_habilitada(cfg, "fiestas_recurrentes"):
        fuentes_usadas.append("fiestas_recurrentes")
        for ev in _load(_FIESTAS).get("eventos", []):
            if ev.get("fecha_inicio"):
                fi = ev.get("fecha_inicio")
                ff = ev.get("fecha_fin") or fi
                try:
                    d_ini = date.fromisoformat(str(fi)[:10])
                    d_fin = date.fromisoformat(str(ff)[:10])
                except ValueError:
                    continue
                if d_fin < hoy or d_ini > hasta:
                    continue
                if not evento_permitido_por_fuentes(ev, cfg):
                    continue
                merge({**ev, "fecha_inicio": d_ini.isoformat(), "fecha_fin": d_fin.isoformat(), "fuente": "fiestas_recurrentes_extendido.json"})
            else:
                for x in _expandir_recurrente(ev, hoy, hasta):
                    if evento_permitido_por_fuentes(x, cfg):
                        merge(x)

    if fuente_habilitada(cfg, "turismo_seed"):
        fuentes_usadas.append("turismo_seed")
        for ev in _eventos_desde_seed_turismo(hoy, hasta):
            if evento_permitido_por_fuentes(ev, cfg):
                merge(ev)

    feriados_n = 0
    if fuente_habilitada(cfg, "feriados_argentina"):
        fuentes_usadas.append("feriados_argentina")
        feriados_n = _merge_feriados(hoy, hasta, merge)

    cordoba_meta: dict[str, Any] = {}
    web_n = 0
    if scrape_web and fuente_habilitada(cfg, "cordoba_turismo"):
        fuentes_usadas.append("cordoba_turismo")
        cordoba = _recolectar_cordoba_turismo(hoy, hasta)
        cordoba_meta = {
            "metodo": cordoba.get("metodo"),
            "error": cordoba.get("error"),
            "total_bruto": cordoba.get("total_bruto"),
            "total_relevantes_bialet": cordoba.get("total_relevantes"),
            "auditoria": cordoba.get("auditoria_path"),
        }
        for w in cordoba.get("relevantes") or []:
            merge(w)
            web_n += 1
    elif scrape_web:
        cordoba_meta = {"omitido": True, "motivo": "cordoba_turismo deshabilitado en configurador"}

    referencia_manual = [
        f["nombre"]
        for f in _flatten_fuentes_catalogo()
        if fuente_habilitada(cfg, f["id"]) and f.get("estado_scraper") == "referencia"
    ]
    for c in cfg.get("fuentes_personalizadas") or []:
        if c.get("habilitada"):
            referencia_manual.append(c.get("nombre", "Personalizada"))

    from ama.engine.evento_fechas import filtrar_items_calendario_diario, filtrar_solo_confirmados

    items = filtrar_items_calendario_diario(items)
    items = filtrar_solo_confirmados(items, hoy=date.today(), desde_consulta=hoy)
    items.sort(
        key=lambda x: (
            x.get("fecha_inicio") or x.get("mes_referencia") or "9999",
            x.get("prioridad") if x.get("prioridad") is not None else 9,
        )
    )

    fuentes_doc = _load(_FUENTES)
    payload = {
        "actualizado_en": datetime.now(timezone.utc).isoformat(),
        "desde": hoy.isoformat(),
        "hasta": hasta.isoformat(),
        "total": len(items),
        "fuentes_consultadas": {
            "habilitadas_scrape": sorted(set(fuentes_usadas)),
            "referencia_revisar_manual": referencia_manual,
            "feriados_puentes": feriados_n,
            "cordoba_turismo": cordoba_meta,
            "eventos_cordoba_turismo_relevantes": web_n,
        },
        "items": items,
    }
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    with _CACHE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    fotos: dict[str, Any] = {"descargadas": 0, "mensaje": "Sin descarga de imágenes"}
    try:
        from ama.scrapers.event_image_fetcher import descargar_desde_confirmados_y_cache

        fotos = descargar_desde_confirmados_y_cache(desde=hoy, hasta=hasta, max_descargas=15)
    except Exception as exc:
        fotos = {"ok": False, "mensaje": f"Fotos web: error ({exc})"}

    return {
        "ok": True,
        "desde": hoy.isoformat(),
        "hasta": hasta.isoformat(),
        "total": len(items),
        "cache": str(_CACHE.name),
        "cordoba_turismo": cordoba_meta,
        "eventos_cordoba_turismo": web_n,
        "fuentes_usadas": fuentes_usadas,
        "referencia_manual": referencia_manual,
        "fotos_web": fotos,
        "mensaje": (
            f"Agenda actualizada: {len(items)} eventos entre "
            f"{hoy.strftime('%d/%m/%Y')} y {hasta.strftime('%d/%m/%Y')}. "
            + (fotos.get("mensaje") or "")
        ),
    }


def leer_cache() -> dict:
    return _load(_CACHE)


def _flatten_fuentes_catalogo() -> list[dict]:
    from backend.services.fuentes_eventos_service import _flatten_catalogo

    return _flatten_catalogo()
