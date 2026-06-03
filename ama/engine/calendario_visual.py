"""
Vista mensual tipo Google Calendar — bloques de hitos + publicaciones por día.
"""
from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from typing import Any

_MESES = (
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)

_DIAS_SEM = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")

_PALETA = {
    "finde_largo": {"color": "#ea580c", "fondo": "#ffedd5", "etiqueta": "Finde largo"},
    "vacaciones_invierno": {"color": "#2563eb", "fondo": "#dbeafe", "etiqueta": "Vacaciones invierno"},
    "vacaciones_verano": {"color": "#ca8a04", "fondo": "#fef9c3", "etiqueta": "Vacaciones verano"},
    "dia_especial": {"color": "#db2777", "fondo": "#fce7f3", "etiqueta": "Día especial"},
    "feriado_nacional": {"color": "#dc2626", "fondo": "#fee2e2", "etiqueta": "Feriado"},
    "evento_local": {"color": "#059669", "fondo": "#d1fae5", "etiqueta": "Evento local"},
    "default": {"color": "#64748b", "fondo": "#f1f5f9", "etiqueta": "Campaña"},
}


def _parse_iso(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def _estilo_hito(tipo: str | None) -> dict[str, str]:
    t = (tipo or "").lower()
    return _PALETA.get(t, _PALETA["default"])


def _formato_publicacion(pieza: dict) -> tuple[str, str]:
    """canal, formato: instagram reel|carousel|post · whatsapp status."""
    ventana = pieza.get("ventana") or ""
    tipo = pieza.get("tipo_pieza") or ""
    if ventana == "t_post" or "status" in (pieza.get("formato") or ""):
        return "whatsapp", "status"
    if ventana in ("t60", "t30") or tipo == "recordatorio_suave":
        return "instagram", "carousel"
    if tipo in ("promo_cta", "urgencia_lastminute"):
        return "instagram", "reel"
    if tipo == "utilidad":
        return "instagram", "post"
    fmt = pieza.get("formato") or "reel"
    return pieza.get("canal") or "instagram", fmt


def _labels_publicacion(canal: str, formato: str) -> tuple[str, str]:
    canal_label = "WhatsApp" if canal == "whatsapp" else "Instagram"
    fmt_map = {
        "reel": "Reel",
        "carousel": "Carrusel",
        "post": "Post",
        "status": "Status",
    }
    return canal_label, fmt_map.get(formato, formato.capitalize())


def _asignar_carriles_barras(barras: list[dict]) -> list[dict]:
    """Apila barras que se solapan en la misma semana (varios eventos a la vez)."""
    if not barras:
        return barras
    ordenadas = sorted(barras, key=lambda x: (x["col_inicio"], -x["span"]))
    fin_por_carril: list[int] = []
    for bar in ordenadas:
        carril = 0
        for i, fin in enumerate(fin_por_carril):
            if bar["col_inicio"] > fin:
                carril = i
                fin_por_carril[i] = bar["col_fin"]
                break
        else:
            carril = len(fin_por_carril)
            fin_por_carril.append(bar["col_fin"])
        bar["carril"] = carril
    return ordenadas


def _acortar_jurisdiccion(nombre: str | None) -> str:
    if not nombre:
        return ""
    n = nombre.replace("Vacaciones invierno — ", "").replace("Vacaciones invierno - ", "")
    mapa = {
        "Provincia de Buenos Aires": "PBA",
        "Ciudad Autónoma de Buenos Aires": "CABA",
        "Santa Fe": "Sta Fe",
        "Entre Ríos": "Entre Ríos",
        "Neuquén / Patagonia norte": "Neuquén",
    }
    for largo, corto in mapa.items():
        if largo in n:
            return corto
    if "—" in n:
        return n.split("—")[-1].strip()[:18]
    return n[:22]


def _merge_barras_vacaciones(
    semana: list[dict],
    bloques: list[dict],
    etiqueta_vista: set[str],
) -> tuple[list[dict], list[dict]]:
    """Un solo chorizo por semana y tipo de vacaciones (todas las provincias juntas)."""
    vac_tipos = frozenset({"vacaciones_invierno", "vacaciones_verano"})
    otros = [b for b in bloques if (b.get("tipo") or "") not in vac_tipos]

    barras: list[dict] = []
    for tipo_vac in ("vacaciones_invierno", "vacaciones_verano"):
        vac = [b for b in bloques if (b.get("tipo") or "") == tipo_vac]
        if not vac:
            continue
        cols: list[int] = []
        juris: list[str] = []
        for b in vac:
            fi = _parse_iso(b["fecha_inicio"])
            ff = _parse_iso(b["fecha_fin"])
            tocado = False
            for i, celda in enumerate(semana):
                fd = _parse_iso(celda.get("fecha"))
                if fd and fi and ff and fi <= fd <= ff:
                    cols.append(i)
                    tocado = True
            if tocado:
                juris.append(_acortar_jurisdiccion(b.get("nombre")))
        if not cols:
            continue
        col_inicio, col_fin = min(cols), max(cols)
        fd0 = _parse_iso(semana[0]["fecha"])
        fd6 = _parse_iso(semana[6]["fecha"])
        fi_min = min(_parse_iso(b["fecha_inicio"]) for b in vac if _parse_iso(b["fecha_inicio"]))
        ff_max = max(_parse_iso(b["fecha_fin"]) for b in vac if _parse_iso(b["fecha_fin"]))
        key = f"vac-unificado|{tipo_vac}|{semana[0]['fecha']}"
        mostrar = key not in etiqueta_vista
        if mostrar:
            etiqueta_vista.add(key)
        etiqueta = "Vacaciones invierno" if tipo_vac == "vacaciones_invierno" else "Vacaciones verano"
        uniq = ", ".join(dict.fromkeys(j for j in juris if j))
        barras.append(
            {
                "hito_id": key,
                "nombre": f"{etiqueta} · {uniq}" if uniq else etiqueta,
                "tipo": tipo_vac,
                "color": vac[0]["color"],
                "fondo": vac[0]["fondo"],
                "col_inicio": col_inicio,
                "col_fin": col_fin,
                "span": col_fin - col_inicio + 1,
                "mostrar_etiqueta": mostrar,
                "continua_antes": bool(fd0 and fi_min and fi_min < fd0),
                "continua_despues": bool(fd6 and ff_max and ff_max > fd6),
                "unificado": True,
            }
        )

    for b in otros:
        fi = _parse_iso(b["fecha_inicio"])
        ff = _parse_iso(b["fecha_fin"])
        if not fi or not ff:
            continue
        cols = [
            i
            for i, celda in enumerate(semana)
            if (fd := _parse_iso(celda.get("fecha"))) and fi <= fd <= ff
        ]
        if not cols:
            continue
        col_inicio, col_fin = min(cols), max(cols)
        hid = b["hito_id"]
        mostrar = hid not in etiqueta_vista
        if mostrar:
            etiqueta_vista.add(hid)
        fd0 = _parse_iso(semana[0]["fecha"])
        fd6 = _parse_iso(semana[6]["fecha"])
        barras.append(
            {
                "hito_id": hid,
                "nombre": b.get("nombre"),
                "tipo": b.get("tipo"),
                "color": b["color"],
                "fondo": b["fondo"],
                "col_inicio": col_inicio,
                "col_fin": col_fin,
                "span": col_fin - col_inicio + 1,
                "mostrar_etiqueta": mostrar,
                "continua_antes": bool(fd0 and fi < fd0),
                "continua_despues": bool(fd6 and ff > fd6),
            }
        )
    return _asignar_carriles_barras(barras), barras


def _barras_para_semana(semana: list[dict], bloques: list[dict], etiqueta_vista: set[str]) -> list[dict]:
    barras, _ = _merge_barras_vacaciones(semana, bloques, etiqueta_vista)
    return barras


def _fechas_barra_visual(fi: date, ff: date, tipo: str | None) -> tuple[date, date]:
    """Finde largo: barra solo vie–sáb–dom (noches alquilables). Resto: rango completo."""
    if (tipo or "").lower() != "finde_largo":
        return fi, ff
    validos: list[date] = []
    d = fi
    while d <= ff:
        if d.weekday() in (4, 5, 6):
            validos.append(d)
        d += timedelta(days=1)
    if not validos:
        return fi, ff
    return min(validos), max(validos)


def _solapa(fi: date, ff: date, inicio: date, fin: date) -> bool:
    return fi <= fin and ff >= inicio


def construir_calendario_visual_mes(
    *,
    anio: int,
    mes: int,
    db: Any | None = None,
) -> dict[str, Any]:
    from ama.engine.plan_marketing_unificado import construir_plan_marketing

    if not 1 <= mes <= 12:
        raise ValueError("Mes inválido")

    plan = construir_plan_marketing(db=db, anio=anio, mes=mes, dias=400)
    hitos: list[dict] = plan.get("hitos") or []

    primer_dia = date(anio, mes, 1)
    ultimo_dia = date(anio, mes, monthrange(anio, mes)[1])

    bloques: list[dict] = []
    pubs_por_dia: dict[str, list[dict]] = defaultdict(list)
    conteo_campaña: dict[str, int] = defaultdict(int)

    for h in hitos:
        fi = _parse_iso(h.get("fecha_inicio"))
        ff = _parse_iso(h.get("fecha_fin")) or fi
        if not fi:
            continue
        estilo = _estilo_hito(h.get("tipo"))
        if _solapa(fi, ff, primer_dia, ultimo_dia):
            bar_fi, bar_ff = _fechas_barra_visual(fi, ff, h.get("tipo"))
            if not _solapa(bar_fi, bar_ff, primer_dia, ultimo_dia):
                bar_fi, bar_ff = fi, ff
            bloques.append(
                {
                    "hito_id": h["id"],
                    "nombre": h.get("nombre"),
                    "tipo": h.get("tipo"),
                    "fecha_inicio": bar_fi.isoformat(),
                    "fecha_fin": bar_ff.isoformat(),
                    "color": estilo["color"],
                    "fondo": estilo["fondo"],
                    "etiqueta_tipo": estilo["etiqueta"],
                    "estrategia": h.get("estrategia"),
                    "total_publicaciones": len(h.get("piezas") or []),
                }
            )

        for p in h.get("piezas") or []:
            fp = _parse_iso(p.get("fecha_publicacion"))
            if not fp or not _solapa(fp, fp, primer_dia, ultimo_dia):
                continue
            canal, formato = _formato_publicacion(p)
            canal_label, formato_label = _labels_publicacion(canal, formato)
            conteo_campaña[h["id"]] += 1
            pubs_por_dia[fp.isoformat()].append(
                {
                    "pieza_id": p.get("id"),
                    "hito_id": h["id"],
                    "hito_nombre": h.get("nombre"),
                    "titulo": p.get("titulo_publicacion"),
                    "fecha": fp.isoformat(),
                    "fecha_legible": p.get("fecha_legible"),
                    "ventana_label": p.get("ventana_label"),
                    "tipo_pieza_label": p.get("tipo_pieza_label"),
                    "estado": p.get("estado"),
                    "canal": canal,
                    "formato": formato,
                    "canal_label": canal_label,
                    "formato_label": formato_label,
                    "color": estilo["color"],
                    "desarrollado": p.get("desarrollado", False),
                }
            )

    # Contenido editorial diario (fidelización, río, sierras — sin evento)
    from ama.engine.piezas_editoriales import listar_piezas_editoriales

    for ep in listar_piezas_editoriales(primer_dia, ultimo_dia):
        fp = _parse_iso(ep.get("fecha"))
        if not fp:
            continue
        # No duplicar si ya hay pieza editorial ese día
        existentes = pubs_por_dia.get(fp.isoformat(), [])
        if any(p.get("es_editorial") for p in existentes):
            continue
        pubs_por_dia[fp.isoformat()].append(ep)

    # Grilla: semanas desde lunes
    grid_start = primer_dia - timedelta(days=primer_dia.weekday())
    grid_end = ultimo_dia + timedelta(days=(6 - ultimo_dia.weekday()))
    semanas: list[list[dict]] = []
    cursor = grid_start
    semana: list[dict] = []

    while cursor <= grid_end:
        ymd = cursor.isoformat()
        en_mes = cursor.month == mes
        bloques_dia = [
            b
            for b in bloques
            if _parse_iso(b["fecha_inicio"]) <= cursor <= _parse_iso(b["fecha_fin"])
        ]
        pubs = pubs_por_dia.get(ymd, [])
        pubs.sort(key=lambda x: (0 if x["canal"] == "instagram" else 1, x.get("titulo") or ""))

        semana.append(
            {
                "fecha": ymd,
                "dia": cursor.day,
                "dia_semana": cursor.weekday(),
                "en_mes": en_mes,
                "es_hoy": cursor == date.today(),
                "bloques": bloques_dia,
                "publicaciones": pubs,
                "total_publicaciones": len(pubs),
            }
        )
        if len(semana) == 7:
            semanas.append(semana)
            semana = []
        cursor += timedelta(days=1)

    # Barras fusionadas (merge cells) por fila de semana
    etiqueta_vista: set[str] = set()
    semanas_con_barras: list[dict] = []
    for sem in semanas:
        barras = _barras_para_semana(sem, bloques, etiqueta_vista)
        max_carril = max((b.get("carril", 0) for b in barras), default=0)
        semanas_con_barras.append(
            {
                "dias": sem,
                "barras": barras,
                "filas_eventos": max_carril + 1 if barras else 0,
            }
        )

    leyenda = []
    tipos_vistos: set[str] = set()
    for b in bloques:
        t = b.get("tipo") or "default"
        if t in tipos_vistos:
            continue
        tipos_vistos.add(t)
        est = _estilo_hito(t)
        leyenda.append(
            {
                "tipo": t,
                "etiqueta": est["etiqueta"],
                "color": est["color"],
                "fondo": est["fondo"],
            }
        )

    resumen_campañas = []
    for b in bloques:
        hid = b["hito_id"]
        resumen_campañas.append(
            {
                **b,
                "publicaciones_en_mes": sum(
                    1
                    for dia in pubs_por_dia.values()
                    for p in dia
                    if p["hito_id"] == hid
                ),
                "publicaciones_totales": b.get("total_publicaciones") or 0,
            }
        )

    leyenda.append(
        {
            "tipo": "editorial",
            "etiqueta": "Editorial diario",
            "color": "#64748b",
            "fondo": "#f1f5f9",
        }
    )

    return {
        "anio": anio,
        "mes": mes,
        "mes_label": _MESES[mes - 1],
        "titulo": f"{_MESES[mes - 1]} {anio}",
        "dias_semana": list(_DIAS_SEM),
        "semanas": semanas_con_barras,
        "semanas_legacy": semanas,
        "bloques_mes": bloques,
        "leyenda": leyenda,
        "campañas": resumen_campañas,
        "total_publicaciones_mes": sum(len(v) for v in pubs_por_dia.values()),
        "filtro_eventos": plan.get("filtro_eventos"),
    }
