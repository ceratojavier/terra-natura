"""
Fechas reales para el calendario — no pintar un mes entero si no hay día confirmado.
"""
from __future__ import annotations

import json
import re
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"
_MAX_DIAS_EN_GRILLA = 21

_ESTADOS_SOLO_LISTADO = frozenset(
    {
        "estacional",
        "ventana_monitoreo",
        "solo_referencia",
        "a_confirmar",
        "titulo_web_sin_fecha",
        "referencia_historica",
        "estimado",
        "estimado_anual",
        "fecha_estimada",
        "recurrente_anual",
        "fecha_referencial_aprox",
    }
)

_TIPOS_OFICIALES = frozenset(
    {
        "feriado_nacional",
        "finde_largo",
        "vacaciones_invierno",
        "promo_invierno",
        "dia_especial",
    }
)

_CONFIRMADO_OK = frozenset({"confirmado", "confirmado_oficial", "oficial"})


def _load_feriados() -> dict:
    p = _DATA / "feriados_puentes_ar.json"
    if not p.is_file():
        return {}
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def _parse_iso(d: str | date | None) -> date | None:
    if d is None:
        return None
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d)[:10])
    except ValueError:
        return None


def _carnaval_rango(anio: int) -> tuple[date, date] | None:
    """Usa el finde largo de Carnaval del JSON de puentes."""
    for pu in _load_feriados().get("fines_de_semana_largo", []):
        if "carnaval" not in (pu.get("nombre") or "").lower():
            continue
        ini = _parse_iso(pu.get("fecha_inicio"))
        fin = _parse_iso(pu.get("fecha_fin"))
        if ini and ini.year == anio:
            return ini, fin or ini
    return None


def _ultimo_sabado(anio: int, mes: int) -> date:
    ult = monthrange(anio, mes)[1]
    d = date(anio, mes, ult)
    while d.weekday() != 5:
        d -= timedelta(days=1)
    return d


def _dia_desde_aprox(dia_aprox: str | None, anio: int, mes: int) -> tuple[date, date] | None:
    if not dia_aprox:
        return None
    t = dia_aprox.lower().strip()

    if "carnaval" in t:
        return _carnaval_rango(anio)

    m = re.search(r"(\d{1,2})\s*(?:de\s+)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)", t)
    if m:
        meses = {
            "enero": 1,
            "febrero": 2,
            "marzo": 3,
            "abril": 4,
            "mayo": 5,
            "junio": 6,
            "julio": 7,
            "agosto": 8,
            "septiembre": 9,
            "octubre": 10,
            "noviembre": 11,
            "diciembre": 12,
        }
        d = int(m.group(1))
        mo = meses.get(m.group(2), mes)
        try:
            unico = date(anio, mo, d)
            return unico, unico
        except ValueError:
            return None

    if "último sábado" in t or "ultimo sabado" in t:
        sab = _ultimo_sabado(anio, mes)
        return sab, sab

    if "mediados" in t and "enero" in t:
        return date(anio, 1, 14), date(anio, 1, 22)

    if "última semana" in t and "mayo" in t:
        return date(anio, 5, 23), date(anio, 5, 30)

    if "últimas 3 semanas enero" in t or "9 lunas" in t:
        return date(anio, 1, 20), date(anio, 2, 1)

    if "semana santa" in t:
        # Viernes Santo aproximado — abril
        return date(anio, 4, 2), date(anio, 4, 5)

    if "sep/oct" in t or "varias fechas" in t or "todo el año" in t or "confirmar" in t:
        return None

    if "feb" in t and "3 días" in t:
        return date(anio, 2, 12), date(anio, 2, 14)

    if "primavera" in t:
        return date(anio, 3, 15), date(anio, 3, 15)

    return None


def _duracion_ok(ini: date, fin: date) -> bool:
    return (fin - ini).days + 1 <= _MAX_DIAS_EN_GRILLA


def fechas_para_calendario(ev: dict, anio: int) -> dict | None:
    """
    Devuelve copia del evento con fecha_inicio/fin reales y flags.
    None = no incluir en agenda.
    """
    out = dict(ev)
    estado = (ev.get("estado") or "").lower()
    categoria = (ev.get("categoria") or "").lower()

    if categoria == "temporada":
        return None

    if estado in _ESTADOS_SOLO_LISTADO and not ev.get("fecha_inicio"):
        out["solo_listado"] = True
        out["mostrar_en_calendario"] = False
        return out

    fi = _parse_iso(ev.get("fecha_inicio"))
    ff = _parse_iso(ev.get("fecha_fin")) or fi

    if fi and ff:
        if fi.year != anio and ff.year != anio:
            if ev.get("mes_inicio"):
                fi = fi.replace(year=anio)
                ff = ff.replace(year=anio)
            else:
                return None
        if not _duracion_ok(fi, ff):
            out["fecha_inicio"] = fi.isoformat()
            out["fecha_fin"] = ff.isoformat()
            out["solo_listado"] = True
            out["mostrar_en_calendario"] = False
            out["nota_calendario"] = "Rango muy amplio — confirmar fecha exacta en fuente oficial"
            return out
        out["fecha_inicio"] = fi.isoformat()
        out["fecha_fin"] = ff.isoformat()
        out["mostrar_en_calendario"] = True
        return out

    mes_i = ev.get("mes_inicio")
    if not mes_i:
        return None

    mes_f = ev.get("mes_fin") or mes_i
    if mes_f - mes_i > 1 and not ev.get("dia_aprox"):
        return None

    rango = _dia_desde_aprox(ev.get("dia_aprox"), anio, mes_i)
    if not rango and mes_i == mes_f:
        # Un solo mes sin día: no inventar 28 días
        if "carnaval" in (ev.get("nombre") or "").lower():
            rango = _carnaval_rango(anio)
        if not rango:
            out["solo_listado"] = True
            out["mostrar_en_calendario"] = False
            out["mes_referencia"] = f"{anio}-{mes_i:02d}"
            out["nota_calendario"] = "Sin fecha exacta — aparece solo en listado hasta confirmar"
            return out

    if not rango:
        return None

    ini, fin = rango
    if not _duracion_ok(ini, fin):
        out["solo_listado"] = True
        out["mostrar_en_calendario"] = False
        out["fecha_inicio"] = ini.isoformat()
        out["fecha_fin"] = fin.isoformat()
        return out

    out["fecha_inicio"] = ini.isoformat()
    out["fecha_fin"] = fin.isoformat()
    out["mostrar_en_calendario"] = True
    out["estado"] = ev.get("estado") or "fecha_estimada"
    return out


def filtrar_items_calendario_diario(items: list[dict]) -> list[dict]:
    """Quita o marca ítems que no deben repetirse en cada día del calendario."""
    limpio = []
    for it in items:
        if it.get("mostrar_en_calendario") is False or it.get("solo_listado"):
            it = dict(it)
            it["tipo"] = it.get("tipo") or "referencia"
            if it.get("tipo") not in ("referencia",):
                it["tipo"] = "referencia"
            limpio.append(it)
            continue
        fi = _parse_iso(it.get("fecha_inicio") or it.get("fecha"))
        ff = _parse_iso(it.get("fecha_fin")) or fi
        if not fi:
            continue
        if not _duracion_ok(fi, ff) and it.get("tipo") not in (
            "finde_largo",
            "vacaciones_invierno",
            "promo_invierno",
        ):
            dup = dict(it)
            dup["solo_listado"] = True
            dup["mostrar_en_calendario"] = False
            dup["tipo"] = "referencia"
            limpio.append(dup)
            continue
        limpio.append(it)
    return limpio


def evento_es_confirmado(
    ev: dict,
    *,
    hoy: date | None = None,
    desde_consulta: date | None = None,
) -> bool:
    """Feriados/puentes oficiales + eventos con estado confirmado y fechas exactas."""
    if ev.get("solo_listado") or ev.get("tipo") == "referencia":
        return False
    tipo = ev.get("tipo") or ""
    if tipo in _TIPOS_OFICIALES:
        return True
    estado = (ev.get("estado") or "").strip().lower()
    if estado in _ESTADOS_SOLO_LISTADO or estado == "confirmado_pasado":
        return False
    # Sin estado explícito NO es confirmado (evita ficticios del cache web)
    if not estado:
        return False
    if estado not in _CONFIRMADO_OK:
        return False
    fi = _parse_iso(ev.get("fecha_inicio") or ev.get("fecha"))
    ff = _parse_iso(ev.get("fecha_fin")) or fi
    if not fi:
        return False
    # Ocultar solo si terminó ANTES del inicio del rango pedido (no por “hoy”)
    ref = desde_consulta or hoy or date.today()
    if ff and ff < ref and tipo not in _TIPOS_OFICIALES:
        return False
    return True


def filtrar_solo_confirmados(
    items: list[dict],
    *,
    hoy: date | None = None,
    desde_consulta: date | None = None,
) -> list[dict]:
    from ama.engine.evento_relevancia_bialet import filtrar_demanda_cabana

    confirmados = [
        it for it in items if evento_es_confirmado(it, hoy=hoy, desde_consulta=desde_consulta)
    ]
    return filtrar_demanda_cabana(confirmados)
