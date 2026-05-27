"""
Coeficiente de inflación variable por fecha — Terra Natura.

No es un % anual fijo: cada período (puente junio, vacaciones julio, verano ene, etc.)
usa inflación acumulada **mismo tramo interanual** (ej. jun-2025 → jun-2026).

Fuente mensual: REM BCRA (mediana consultoras) + fallback si falta un mes.
"""
from __future__ import annotations

import io
import json
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, timedelta
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent.parent
_CACHE = _REPO / "local" / "inflacion_proyeccion_cache.json"
_FALLBACK = _REPO / "ama" / "data" / "inflacion_fuentes_fallback.json"
_BCRA_REM = "https://www.bcra.gob.ar/relevamiento-expectativas-mercado-rem/"
_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_TASA_MENSUAL_DEFAULT = 2.6  # % si no hay dato REM para ese mes


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _fetch_url(url: str, timeout: int = 35) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TerraNatura-PMS/1.0 (coeficiente inflación)"},
    )
    with urllib.request.urlopen(req, context=_ssl_ctx(), timeout=timeout) as resp:
        return resp.read()


def _excel_serial_a_fecha(serial: str | float) -> date | None:
    try:
        n = int(float(serial))
    except (TypeError, ValueError):
        return None
    if n < 40000 or n > 60000:
        return None
    return date(1899, 12, 30) + timedelta(days=n)


def _periodo_key(d: date) -> str:
    return f"{d.year}-{d.month:02d}"


def _parsear_periodo_key(key: str) -> tuple[int, int]:
    y, m = key.split("-")
    return int(y), int(m)


def _mes_siguiente(y: int, m: int) -> tuple[int, int]:
    if m >= 12:
        return y + 1, 1
    return y, m + 1


def _descubrir_xlsx_rem() -> tuple[str, str] | None:
    html = _fetch_url(_BCRA_REM).decode("utf-8", "ignore")
    matches = re.findall(
        r'href="(/archivos/Pdfs/PublicacionesEstadisticas/informes/tablas-relevamiento-expectativas-mercado-([a-z]{3})-(\d{4})\.xlsx)"',
        html,
        flags=re.I,
    )
    if not matches:
        return None
    path, mes, anio = matches[0]
    return f"https://www.bcra.gob.ar{path}", f"{mes.lower()}-{anio}"


def _parsear_serie_mensual_rem(xlsx_bytes: bytes) -> dict[str, float]:
    """IPC nivel general — mediana mensual proyectada (columna D, filas mensuales)."""
    z = zipfile.ZipFile(io.BytesIO(xlsx_bytes))
    ss: list[str] = []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    for si in root.findall(".//m:si", _NS):
        ss.append("".join((t.text or "") for t in si.findall(".//m:t", _NS)))

    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    cells: dict[str, str] = {}
    for c in sheet.findall(".//m:c", _NS):
        ref = c.attrib.get("r", "")
        v = c.find("m:v", _NS)
        if v is None or v.text is None:
            continue
        val = v.text
        if c.attrib.get("t") == "s":
            val = ss[int(val)]
        cells[ref] = val

    serie: dict[str, float] = {}
    for ref, raw in cells.items():
        col = "".join(ch for ch in ref if ch.isalpha())
        row_s = "".join(ch for ch in ref if ch.isdigit())
        if col != "D" or not row_s:
            continue
        c_val = str(cells.get(f"C{row_s}", "")).lower()
        if "mensual" not in c_val:
            continue
        try:
            tasa = float(str(raw).replace(",", "."))
        except ValueError:
            continue
        if not (0 < tasa < 15):
            continue

        b_raw = cells.get(f"B{row_s}", "")
        fd = _excel_serial_a_fecha(b_raw)
        if fd:
            serie[_periodo_key(fd)] = tasa

    return serie


def _cargar_fallback() -> dict[str, Any]:
    if _FALLBACK.is_file():
        try:
            return json.loads(_FALLBACK.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"tasa_mensual_default_pct": _TASA_MENSUAL_DEFAULT}


def _guardar_cache(data: dict[str, Any]) -> None:
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    _CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _leer_cache(max_edad_horas: int = 36) -> dict[str, Any] | None:
    if not _CACHE.is_file():
        return None
    try:
        data = json.loads(_CACHE.read_text(encoding="utf-8"))
        ts = data.get("actualizado")
        if not ts:
            return data
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if (datetime.now(timezone.utc) - dt).total_seconds() / 3600 <= max_edad_horas:
            return data
    except Exception:
        pass
    return None


def actualizar_serie_rem(forzar: bool = False) -> dict[str, Any]:
    if not forzar:
        c = _leer_cache()
        if c and c.get("serie_mensual"):
            return c

    fb = _cargar_fallback()
    out: dict[str, Any] = {
        "actualizado": _utc_now(),
        "ok": False,
        "serie_mensual": {},
        "tasa_default_pct": fb.get("tasa_mensual_default_pct", _TASA_MENSUAL_DEFAULT),
    }
    try:
        found = _descubrir_xlsx_rem()
        if not found:
            raise ValueError("Sin enlace XLSX REM")
        url, periodo = found
        serie = _parsear_serie_mensual_rem(_fetch_url(url))
        if not serie:
            raise ValueError("No se extrajo serie mensual del XLSX")
        out.update(
            {
                "ok": True,
                "serie_mensual": serie,
                "rem_url": url,
                "rem_periodo": periodo,
                "fuente": f"REM BCRA mediana mensual IPC ({periodo})",
            }
        )
    except Exception as e:
        out["error"] = str(e)
        out["fuente"] = "fallback"

    _guardar_cache(out)
    return out


def _tasa_mensual(y: int, m: int, cache: dict[str, Any] | None = None) -> float:
    c = cache or _leer_cache() or actualizar_serie_rem()
    serie = c.get("serie_mensual") or {}
    key = f"{y}-{m:02d}"
    if key in serie:
        return float(serie[key])
    return float(c.get("tasa_default_pct", _TASA_MENSUAL_DEFAULT))


def coeficiente_interanual_mismo_mes(fecha: date, cache: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Multiplicador de precio base → fecha objetivo.
    Acumula inflación mensual REM desde (año-1, mes) hasta (año, mes) inclusive.

    Ej.: puente 20-jun-2026 → coef. jun-2025…jun-2026 (≠ jul vacaciones ≠ dic).
    """
    if cache is None:
        cache = _leer_cache() or actualizar_serie_rem()

    y, m = fecha.year, fecha.month
    y0, m0 = y - 1, m
    mult = 1.0
    meses_detalle: list[dict[str, Any]] = []

    cy, cm = y0, m0
    while True:
        tasa = _tasa_mensual(cy, cm, cache)
        mult *= 1.0 + tasa / 100.0
        meses_detalle.append({"periodo": f"{cy}-{cm:02d}", "tasa_mensual_pct": round(tasa, 2)})
        if (cy, cm) == (y, m):
            break
        cy, cm = _mes_siguiente(cy, cm)

    return {
        "fecha": fecha.isoformat(),
        "multiplicador": round(mult, 6),
        "coeficiente_pct": round((mult - 1.0) * 100.0, 2),
        "metodo": "interanual_mismo_mes_acumulado",
        "desde_periodo": f"{y0}-{m0:02d}",
        "hasta_periodo": f"{y}-{m:02d}",
        "meses": meses_detalle,
        "fuente": cache.get("fuente", "REM BCRA"),
    }


def coeficiente_para_estadia(check_in: date, check_out: date) -> dict[str, Any]:
    """Un coeficiente por noche (cambia si la estadía cruza meses)."""
    noches: list[date] = []
    cur = check_in
    while cur < check_out:
        noches.append(cur)
        cur += timedelta(days=1)

    cache = _leer_cache() or actualizar_serie_rem()
    por_noche = [coeficiente_interanual_mismo_mes(d, cache) for d in noches]
    mult_prom = sum(x["multiplicador"] for x in por_noche) / len(por_noche) if por_noche else 1.0

    return {
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "noches": len(noches),
        "multiplicador_promedio": round(mult_prom, 6),
        "coeficiente_pct_promedio": round((mult_prom - 1.0) * 100.0, 2),
        "por_noche": por_noche,
    }


def vista_previa_periodos(base_alpina: float = 115000, base_suite: float = 87500) -> list[dict[str, Any]]:
    """Ejemplos para el configurador: distintos períodos, distintos coeficientes."""
    hoy = date.today()
    ejemplos = [
        ("Próximo finde largo (jun)", date(hoy.year, 6, 15)),
        ("Vacaciones invierno (jul)", date(hoy.year, 7, 15)),
        ("Verano próximo (ene)", date(hoy.year + (1 if hoy.month > 2 else 0), 1, 10)),
        ("Puente dic / fin de año", date(hoy.year, 12, 28)),
    ]
    cache = _leer_cache() or actualizar_serie_rem()
    filas = []
    for etiqueta, f in ejemplos:
        c = coeficiente_interanual_mismo_mes(f, cache)
        filas.append(
            {
                "etiqueta": etiqueta,
                "fecha_referencia": f.isoformat(),
                "coeficiente_pct": c["coeficiente_pct"],
                "multiplicador": c["multiplicador"],
                "precio_alpina_ejemplo": round(base_alpina * c["multiplicador"]),
                "precio_suite_ejemplo": round(base_suite * c["multiplicador"]),
                "tramo": f"{c['desde_periodo']} → {c['hasta_periodo']}",
            }
        )
    return filas
