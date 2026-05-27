"""
Agenda unificada de fechas importantes — vista previa antes del calendario editorial.
Rango típico: desde HOY hasta fin de marzo del año siguiente (configurable).
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent.parent / "ama" / "data"
_FERIADOS_PUENTES = _DATA / "feriados_puentes_ar.json"
_VACACIONES = _DATA / "vacaciones_invierno_provincias.json"
_IMPORTANTE = _DATA / "calendario_importante_ar.json"


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _fmt_ar(d: date | None) -> str:
    if not d:
        return ""
    return d.strftime("%d/%m/%Y")


def _parse(d: str | None) -> date | None:
    if not d:
        return None
    try:
        return date.fromisoformat(d[:10])
    except ValueError:
        return None


def _en_rango(ini: date | None, fin: date | None, desde: date, hasta: date) -> bool:
    """Intersección con [desde, hasta] — excluye eventos que ya terminaron antes de «desde»."""
    if ini is None and fin is None:
        return False
    start = ini or fin
    end = fin or ini
    if start is None or end is None:
        return False
    if end < desde:
        return False
    if start > hasta:
        return False
    return True


def listar_importantes(
    *,
    desde: date | None = None,
    hasta: date | None = None,
    db: Any | None = None,
    solo_confirmados: bool = True,
) -> dict:
    """
    desde: default hoy
    hasta: default 31 marzo del año siguiente al de «hasta» o al de hoy+10 meses
    """
    inicio = desde or date.today()
    if hasta is None:
        anio_marzo = inicio.year + 1 if inicio.month > 3 else inicio.year
        hasta = date(anio_marzo, 3, 31)

    from ama.engine.puente_travel_context import enriquecer_finde_largo, feriados_en_set

    feriados_set = feriados_en_set(_load(_FERIADOS_PUENTES).get("feriados_nacionales", []))
    imp_pre = _load(_IMPORTANTE)
    for f in imp_pre.get("feriados_nacionales_2027", []):
        if f.get("fecha"):
            feriados_set.add(f["fecha"][:10])

    items: list[dict] = []

    vistos_add: set[str] = set()

    def add(item: dict) -> None:
        key = f"{item.get('nombre','')}|{item.get('fecha_inicio')}|{item.get('fecha')}|{item.get('tipo')}"
        if key in vistos_add:
            return
        vistos_add.add(key)
        item["orden"] = item.get("fecha_inicio") or item.get("fecha") or "9999-99-99"
        items.append(item)

    # Feriados nacionales (JSON puente file + 2027)
    fp = _load(_FERIADOS_PUENTES)
    for f in fp.get("feriados_nacionales", []):
        fd = _parse(f.get("fecha"))
        if fd and inicio <= fd <= hasta:
            add(
                {
                    "tipo": "feriado_nacional",
                    "nombre": f["nombre"],
                    "fecha": fd.isoformat(),
                    "fecha_inicio": fd.isoformat(),
                    "fecha_fin": fd.isoformat(),
                    "categoria": "feriado",
                    "fuente": "feriados_puentes_ar.json",
                }
            )

    for f in imp_pre.get("feriados_nacionales_2027", []):
        fd = _parse(f.get("fecha"))
        if fd and inicio <= fd <= hasta:
            add(
                {
                    "tipo": "feriado_nacional",
                    "nombre": f["nombre"] + " (2027)",
                    "fecha": fd.isoformat(),
                    "fecha_inicio": fd.isoformat(),
                    "fecha_fin": fd.isoformat(),
                    "categoria": "feriado",
                    "fuente": "calendario_importante_ar.json",
                }
            )

    for pu in fp.get("fines_de_semana_largo", []):
        ini, fin = _parse(pu.get("fecha_inicio")), _parse(pu.get("fecha_fin"))
        if _en_rango(ini, fin, inicio, hasta):
            base = {
                "tipo": "finde_largo",
                "nombre": pu.get("nombre"),
                "fecha_inicio": ini.isoformat() if ini else None,
                "fecha_fin": fin.isoformat() if fin else None,
                "noches_sugeridas": pu.get("noches_sugeridas"),
                "copy_hook": pu.get("copy_hook"),
                "categoria": "puente",
                "fuente": "feriados_puentes_ar.json",
            }
            if ini and fin:
                base = enriquecer_finde_largo(base, feriados_set)
            add(base)

    for pu in imp_pre.get("fines_de_semana_largo_2027", []):
        ini, fin = _parse(pu.get("fecha_inicio")), _parse(pu.get("fecha_fin"))
        if _en_rango(ini, fin, inicio, hasta):
            base = {
                "tipo": "finde_largo",
                "nombre": pu.get("nombre"),
                "fecha_inicio": ini.isoformat() if ini else None,
                "fecha_fin": fin.isoformat() if fin else None,
                "noches_sugeridas": pu.get("noches_sugeridas"),
                "copy_hook": pu.get("copy_hook"),
                "categoria": "puente",
                "fuente": "calendario_importante_ar.json",
            }
            if ini and fin:
                base = enriquecer_finde_largo(base, feriados_set)
            add(base)

    vac = _load(_VACACIONES)
    for v in vac.get("vacaciones_invierno", []):
        ini, fin = _parse(v.get("fecha_inicio")), _parse(v.get("fecha_fin"))
        if _en_rango(ini, fin, inicio, hasta):
            add(
                {
                    "tipo": "vacaciones_invierno",
                    "nombre": f"Vacaciones invierno — {v.get('jurisdiccion')}",
                    "fecha_inicio": ini.isoformat() if ini else None,
                    "fecha_fin": fin.isoformat() if fin else None,
                    "mensaje_campana": v.get("mensaje_campana"),
                    "categoria": "vacaciones",
                    "fuente": "vacaciones_invierno_provincias.json",
                }
            )

    for blo in vac.get("bloques_promo_invierno", []):
        ini, fin = _parse(blo.get("desde")), _parse(blo.get("hasta"))
        if _en_rango(ini, fin, inicio, hasta):
            add(
                {
                    "tipo": "promo_invierno",
                    "nombre": blo.get("nombre"),
                    "fecha_inicio": ini.isoformat() if ini else None,
                    "fecha_fin": fin.isoformat() if fin else None,
                    "oferta_sugerida": blo.get("oferta_sugerida"),
                    "categoria": "promo",
                    "fuente": "vacaciones_invierno_provincias.json",
                }
            )

    for d in imp_pre.get("dias_especiales_comerciales", []):
        fd = _parse(d.get("fecha"))
        if fd and inicio <= fd <= hasta:
            add(
                {
                    "tipo": "dia_especial",
                    "nombre": d["nombre"],
                    "fecha": fd.isoformat(),
                    "fecha_inicio": fd.isoformat(),
                    "fecha_fin": fd.isoformat(),
                    "angulo": d.get("angulo"),
                    "nota": d.get("nota"),
                    "categoria": "especial",
                    "fuente": "calendario_importante_ar.json",
                }
            )

    from ama.engine.evento_fechas import fechas_para_calendario, _parse_iso as _piso

    for ev in imp_pre.get("eventos_masivos", []) + imp_pre.get("eventos_locales_bialet", []):
        anio_ref = inicio.year
        norm = fechas_para_calendario(ev, anio_ref)
        if not norm:
            continue
        if norm.get("solo_listado") or norm.get("mostrar_en_calendario") is False:
            add(
                {
                    "tipo": "referencia",
                    "nombre": ev["nombre"],
                    "fecha_inicio": norm.get("fecha_inicio"),
                    "fecha_fin": norm.get("fecha_fin"),
                    "localidad": ev.get("localidad"),
                    "categoria": ev.get("categoria"),
                    "descripcion": ev.get("descripcion") or norm.get("nota_calendario"),
                    "estado": ev.get("estado") or "sin_fecha_exacta",
                    "prioridad": ev.get("prioridad", 5),
                    "tags": ev.get("tags"),
                    "fuente": "calendario_importante_ar.json",
                    "solo_listado": True,
                    "mostrar_en_calendario": False,
                }
            )
            continue
        ini = _piso(norm.get("fecha_inicio"))
        fin = _piso(norm.get("fecha_fin")) or ini
        if ini and _en_rango(ini, fin, inicio, hasta):
            add(
                {
                    "tipo": "evento_masivo" if ev.get("masivo") else "evento_local",
                    "nombre": ev["nombre"],
                    "fecha_inicio": ini.isoformat(),
                    "fecha_fin": fin.isoformat() if fin else ini.isoformat(),
                    "localidad": ev.get("localidad"),
                    "categoria": ev.get("categoria"),
                    "descripcion": ev.get("descripcion"),
                    "estado": norm.get("estado") or ev.get("estado"),
                    "prioridad": ev.get("prioridad"),
                    "tags": ev.get("tags"),
                    "fuente": "calendario_importante_ar.json",
                    "mostrar_en_calendario": True,
                }
            )

    cordoba_stats: dict[str, Any] = {}
    try:
        from ama.scrapers.sources_cordoba_turismo import recolectar_eventos_cordoba_turismo

        ct = recolectar_eventos_cordoba_turismo(desde=inicio, hasta=hasta)
        cordoba_stats = {
            "metodo": ct.get("metodo"),
            "total_bruto": ct.get("total_bruto"),
            "total_relevantes_bialet": ct.get("total_relevantes"),
            "error": ct.get("error"),
            "fuente": "https://cordobaturismo.gov.ar/wp-json/tribe/events/v1/events",
        }
        for ev in ct.get("relevantes") or []:
            ini = _parse(ev.get("fecha_inicio"))
            fin = _parse(ev.get("fecha_fin")) or ini
            if ini and _en_rango(ini, fin, inicio, hasta):
                add(
                    {
                        "tipo": "evento_cordoba_turismo",
                        "nombre": ev["nombre"],
                        "fecha_inicio": ini.isoformat(),
                        "fecha_fin": fin.isoformat() if fin else ini.isoformat(),
                        "localidad": ev.get("localidad"),
                        "categoria": ev.get("categoria"),
                        "descripcion": (ev.get("descripcion") or "")[:300],
                        "angulo_comercial": ev.get("angulo_comercial"),
                        "distancia_km_bialet": ev.get("distancia_km_bialet"),
                        "estado": "confirmado",
                        "prioridad": 2,
                        "fuente": ev.get("fuente"),
                        "fuente_url": ev.get("fuente_url"),
                        "potencial_cabaña": True,
                        "mostrar_en_calendario": True,
                    }
                )
    except Exception as exc:
        cordoba_stats = {"error": str(exc)}

    _confirmados_path = _DATA / "eventos_confirmados_ar.json"
    for ev in _load(_confirmados_path).get("eventos", []):
        ini, fin = _parse(ev.get("fecha_inicio")), _parse(ev.get("fecha_fin"))
        if ini and _en_rango(ini, fin, inicio, hasta):
            add(
                {
                    "tipo": "evento_confirmado",
                    "nombre": ev["nombre"],
                    "fecha_inicio": ini.isoformat(),
                    "fecha_fin": fin.isoformat() if fin else ini.isoformat(),
                    "localidad": ev.get("localidad"),
                    "categoria": ev.get("categoria"),
                    "descripcion": ev.get("descripcion"),
                    "angulo_comercial": ev.get("angulo_comercial"),
                    "distancia_km_bialet": ev.get("distancia_km_bialet"),
                    "masivo": ev.get("masivo"),
                    "estado": "confirmado",
                    "prioridad": ev.get("prioridad", 1),
                    "fuente": ev.get("fuente", "eventos_confirmados_ar.json"),
                    "mostrar_en_calendario": True,
                }
            )

    if not solo_confirmados:
        for ref in imp_pre.get("referencias_monitoreo", []):
            add(
                {
                    "tipo": "referencia",
                    "nombre": ref["nombre"],
                    "fecha_inicio": None,
                    "fecha_fin": None,
                    "localidad": ref.get("localidad"),
                    "descripcion": ref.get("nota") or ref.get("descripcion"),
                    "categoria": ref.get("categoria", "monitoreo"),
                    "fuente": "calendario_importante_ar.json",
                    "solo_listado": True,
                    "mostrar_en_calendario": False,
                    "mes_referencia": ref.get("mes_tipico"),
                }
            )

    # Turismo DB (seed + youtube)
    if db is not None:
        try:
            from backend.models.turismo import TurismoEvento

            for ev in db.query(TurismoEvento).filter(TurismoEvento.activo.is_(True)).all():
                ini = ev.fecha_inicio
                fin = ev.fecha_fin or ini
                if ini and _en_rango(ini, fin, inicio, hasta):
                    add(
                        {
                            "tipo": "evento_grilla",
                            "nombre": ev.nombre,
                            "fecha_inicio": ini.isoformat(),
                            "fecha_fin": fin.isoformat() if fin else ini.isoformat(),
                            "localidad": ev.localidad,
                            "categoria": ev.categoria,
                            "descripcion": (ev.descripcion or "")[:300],
                            "prioridad": ev.prioridad,
                            "tags": ev.tags,
                            "fuente": "turismo_eventos (BD)",
                        }
                    )
                elif ev.mes_inicio and not ini:
                    from ama.engine.evento_fechas import fechas_para_calendario

                    row = {
                        "nombre": ev.nombre,
                        "localidad": ev.localidad,
                        "categoria": ev.categoria,
                        "mes_inicio": ev.mes_inicio,
                        "mes_fin": ev.mes_fin,
                        "dia_aprox": ev.dia_aprox,
                        "descripcion": ev.descripcion,
                        "prioridad": ev.prioridad,
                    }
                    for anio in range(inicio.year, hasta.year + 1):
                        norm = fechas_para_calendario(row, anio)
                        if not norm:
                            continue
                        if norm.get("solo_listado"):
                            add(
                                {
                                    "tipo": "referencia",
                                    "nombre": ev.nombre,
                                    "mes_referencia": f"{anio}-{ev.mes_inicio:02d}",
                                    "localidad": ev.localidad,
                                    "categoria": ev.categoria,
                                    "dia_aprox": ev.dia_aprox,
                                    "descripcion": (norm.get("nota_calendario") or ev.descripcion or "")[:200],
                                    "fuente": "turismo_eventos (BD, sin fecha exacta)",
                                    "solo_listado": True,
                                    "mostrar_en_calendario": False,
                                }
                            )
                            continue
                        fi = _parse(norm.get("fecha_inicio"))
                        ff = _parse(norm.get("fecha_fin")) or fi
                        if fi and _en_rango(fi, ff, inicio, hasta):
                            add(
                                {
                                    "tipo": "evento_grilla",
                                    "nombre": ev.nombre,
                                    "fecha_inicio": fi.isoformat(),
                                    "fecha_fin": ff.isoformat() if ff else fi.isoformat(),
                                    "localidad": ev.localidad,
                                    "categoria": ev.categoria,
                                    "dia_aprox": ev.dia_aprox,
                                    "descripcion": (ev.descripcion or "")[:200],
                                    "fuente": "turismo_eventos (BD)",
                                    "mostrar_en_calendario": True,
                                }
                            )
        except Exception:
            pass

    if not solo_confirmados:
        try:
            from ama.scrapers.event_hunter import leer_cache

            cache = leer_cache()
            for ev in cache.get("items", []):
                if ev.get("solo_listado") or ev.get("mostrar_en_calendario") is False:
                    if ev.get("tipo") == "referencia" or ev.get("solo_listado"):
                        add(
                            {
                                "tipo": "referencia",
                                "nombre": ev["nombre"],
                                "fecha_inicio": ev.get("fecha_inicio"),
                                "fecha_fin": ev.get("fecha_fin"),
                                "localidad": ev.get("localidad"),
                                "categoria": ev.get("categoria"),
                                "descripcion": (ev.get("descripcion") or ev.get("nota_calendario") or "")[:200],
                                "estado": ev.get("estado"),
                                "fuente": ev.get("fuente", "eventos_agenda_cache"),
                                "solo_listado": True,
                                "mostrar_en_calendario": False,
                                "mes_referencia": ev.get("mes_referencia"),
                            }
                        )
                    continue
                ini = _parse(ev.get("fecha_inicio"))
                fin = _parse(ev.get("fecha_fin")) or ini
                if ini and _en_rango(ini, fin, inicio, hasta):
                    from ama.engine.evento_fechas import _duracion_ok

                    if not _duracion_ok(ini, fin):
                        continue
                    add(
                        {
                            "tipo": "evento_agenda",
                            "nombre": ev["nombre"],
                            "fecha_inicio": ini.isoformat(),
                            "fecha_fin": fin.isoformat() if fin else ini.isoformat(),
                            "localidad": ev.get("localidad"),
                            "categoria": ev.get("categoria"),
                            "descripcion": (ev.get("descripcion") or "")[:200],
                            "estado": ev.get("estado"),
                            "prioridad": ev.get("prioridad", 5),
                            "tags": ev.get("tags"),
                            "fuente": ev.get("fuente", "eventos_agenda_cache"),
                            "mostrar_en_calendario": True,
                        }
                    )
        except Exception:
            pass

    def _dedupe_por_nombre_fecha(lst: list[dict]) -> list[dict]:
        prio = {
            "evento_confirmado": 0,
            "evento_masivo": 1,
            "evento_local": 2,
            "evento_cordoba_turismo": 3,
            "finde_largo": 4,
            "feriado_nacional": 5,
            "evento_grilla": 6,
            "evento_agenda": 8,
        }
        mejor: dict[str, dict] = {}
        for it in lst:
            key = f"{(it.get('nombre') or '').strip().lower()}|{(it.get('fecha_inicio') or it.get('fecha') or '')[:10]}"
            if key not in mejor:
                mejor[key] = it
                continue
            t_new = prio.get(it.get("tipo"), 9)
            t_old = prio.get(mejor[key].get("tipo"), 9)
            if t_new < t_old:
                mejor[key] = it
        return list(mejor.values())

    items = _dedupe_por_nombre_fecha(items)

    fuentes_path = _DATA / "fuentes_agenda_eventos.json"
    fuentes_doc = _load(fuentes_path) if fuentes_path.is_file() else {}

    if solo_confirmados:
        from ama.engine.evento_fechas import filtrar_solo_confirmados

        items = filtrar_solo_confirmados(items, hoy=date.today(), desde_consulta=inicio)

    items.sort(key=lambda x: (x.get("orden") or "", x.get("prioridad") if x.get("prioridad") is not None else 9))

    from ama.engine.evento_post_preview import enriquecer_post_preview

    items = [enriquecer_post_preview(it) for it in items]

    por_tipo: dict[str, int] = {}
    for it in items:
        por_tipo[it["tipo"]] = por_tipo.get(it["tipo"], 0) + 1

    por_mes: dict[str, list] = {}
    for it in items:
        key = (it.get("fecha_inicio") or it.get("fecha") or "")[:7]
        if key:
            por_mes.setdefault(key, []).append(it)

    dias_rango = (hasta - inicio).days + 1
    return {
        "desde": inicio.isoformat(),
        "hasta": hasta.isoformat(),
        "dias_en_rango": dias_rango,
        "hoy": date.today().isoformat(),
        "total": len(items),
        "por_tipo": por_tipo,
        "por_mes": {k: por_mes[k] for k in sorted(por_mes.keys())},
        "items": items,
        "fuentes": fuentes_doc,
        "agente_eventos": {
            "cordoba_turismo": cordoba_stats,
            "filtro": "Solo eventos con fecha oficial y potencial estadía en Bialet (Punilla / excursión Córdoba cercana)",
            "doc": "docs/FUENTES_BUSQUEDA_EVENTOS.md",
        },
        "solo_confirmados": solo_confirmados,
        "mensaje": (
            f"Del {_fmt_ar(inicio)} al {_fmt_ar(hasta)} — {len(items)} fechas con "
            + (
                "potencial de reserva en Terra Natura (Punilla o excursión Córdoba/Kempes cercana)"
                if solo_confirmados
                else "referencias incluidas"
            )
            + f". Tocá un día para ver por qué conviene alojarse en Bialet."
        ),
        "desde_fmt": _fmt_ar(inicio),
        "hasta_fmt": _fmt_ar(hasta),
    }
