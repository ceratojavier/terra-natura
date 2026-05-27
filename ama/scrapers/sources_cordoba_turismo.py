"""
Córdoba Turismo — agenda oficial (The Events Calendar REST API).
https://cordobaturismo.gov.ar/wp-json/tribe/events/v1/events

El sitio bloquea bots (403) en muchas redes; estrategia:
1. API con httpx (funciona en algunas IPs)
2. Archivo local ama/data/eventos_cordoba_turismo_sync.json (sync navegador / Playwright)
3. Playwright headless si está instalado (playwright install)
"""
from __future__ import annotations

import json
import re
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"
_SYNC_FILE = _DATA / "eventos_cordoba_turismo_sync.json"
_API = "https://cordobaturismo.gov.ar/wp-json/tribe/events/v1/events"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-AR,es;q=0.9",
    "Referer": "https://cordobaturismo.gov.ar/agenda/",
}

# venue.city / texto → localidad normalizada + km aproximado (criterios_eventos_cabanas.json)
_CIUDAD_ALIASES: list[tuple[re.Pattern[str], str, float | None]] = [
    (re.compile(r"bialet", re.I), "Bialet Massé", 0),
    (re.compile(r"cosqu[ií]n", re.I), "Cosquín", 12),
    (re.compile(r"carlos\s*paz|villa\s*carlos\s*paz", re.I), "Villa Carlos Paz", 18),
    (re.compile(r"san\s*roque|dique", re.I), "San Roque", 12),
    (re.compile(r"la\s*falda", re.I), "La Falda", 28),
    (re.compile(r"la\s*cumbre", re.I), "La Cumbre", 22),
    (re.compile(r"capilla\s*del\s*monte", re.I), "Capilla del Monte", 35),
    (re.compile(r"villa\s*giardino", re.I), "Villa Giardino", 18),
    (re.compile(r"santa\s*mar[ií]a", re.I), "Santa María de Punilla", 8),
    (re.compile(r"tanti", re.I), "Tanti", 25),
    (re.compile(r"valle\s*hermoso", re.I), "Valle Hermoso", 20),
    (re.compile(r"huerta\s*grande", re.I), "Huerta Grande", 25),
    (re.compile(r"belgrano|villa\s*general", re.I), "Villa General Belgrano", 72),
    (re.compile(r"alta\s*gracia", re.I), "Alta Gracia", 48),
    (re.compile(r"c[oó]rdoba(\s*capital)?|capital", re.I), "Córdoba capital", 42),
    (re.compile(r"kempes|estadio|polideportivo|la\s*estaci[oó]n", re.I), "Córdoba capital", 42),
    (re.compile(r"unquillo", re.I), "Unquillo", 55),
    (re.compile(r"rio\s*ceballos", re.I), "Río Ceballos", 50),
    (re.compile(r"jes[uú]s\s*mar[ií]a", re.I), "Jesús María", 65),
    (re.compile(r"villa\s*mar[ií]a", re.I), "Villa María", 120),
    (re.compile(r"rio\s*cuarto", re.I), "Río Cuarto", 200),
    (re.compile(r"de[aá]n\s*funes", re.I), "Deán Funes", 180),
]


def _parse_fecha_api(s: str | None) -> date | None:
    if not s:
        return None
    s = str(s).strip().replace("T", " ")[:19]
    try:
        if len(s) >= 19:
            return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S").date()
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def _strip_html(html: str) -> str:
    if not html:
        return ""
    t = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", t).strip()[:500]


def _inferir_localidad(venue: dict, titulo: str, descripcion: str) -> tuple[str | None, float | None]:
    # Título primero: el venue suele decir "Córdoba" aunque el evento sea en otra ciudad
    partes = [titulo, venue.get("address") or "", venue.get("city") or "", venue.get("venue") or "", descripcion]
    texto = " ".join(partes)
    for pat, loc, km in _CIUDAD_ALIASES:
        if pat.search(texto):
            return loc, km
    return None, None


def _tribe_a_item(raw: dict) -> dict | None:
    titulo = (raw.get("title") or "").strip()
    if not titulo:
        return None
    fi = _parse_fecha_api(raw.get("start_date"))
    ff = _parse_fecha_api(raw.get("end_date")) or fi
    if not fi:
        return None
    venue = raw.get("venue") or {}
    desc = _strip_html(raw.get("description") or "")
    loc, km = _inferir_localidad(venue, titulo, desc)
    return {
        "nombre": titulo[:200],
        "localidad": loc or venue.get("city") or "Córdoba",
        "distancia_km_bialet": km,
        "categoria": "cordoba_turismo",
        "fecha_inicio": fi.isoformat(),
        "fecha_fin": (ff or fi).isoformat(),
        "descripcion": desc[:300] if desc else None,
        "estado": "confirmado",
        "fuente": "cordobaturismo.gov.ar (API agenda)",
        "fuente_url": raw.get("url"),
        "id_externo": str(raw.get("id") or ""),
        "tipo": "evento_cordoba_turismo",
        "mostrar_en_calendario": True,
    }


def _fetch_api_paginado(desde: date, hasta: date) -> tuple[list[dict], str | None]:
    try:
        import httpx
    except ImportError:
        return [], "httpx no instalado"

    todos: list[dict] = []
    err: str | None = None
    with httpx.Client(headers=_HEADERS, follow_redirects=True, timeout=45) as client:
        try:
            client.get("https://cordobaturismo.gov.ar/", timeout=20)
        except Exception:
            pass
        page = 1
        total = 0
        while page <= 30:
            params = {
                "per_page": 50,
                "page": page,
                "start_date": desde.isoformat(),
                "end_date": hasta.isoformat(),
            }
            try:
                r = client.get(_API, params=params)
            except Exception as exc:
                err = str(exc)
                break
            if r.status_code == 403:
                err = "403 WAF — usar sync navegador o Playwright"
                break
            if r.status_code != 200:
                err = f"HTTP {r.status_code}"
                break
            data = r.json()
            total = int(data.get("total") or 0)
            batch = data.get("events") or []
            if not batch:
                break
            todos.extend(batch)
            if len(todos) >= total:
                break
            page += 1
            time.sleep(0.35)
    return todos, err


def _fetch_playwright(desde: date, hasta: date) -> tuple[list[dict], str | None]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return [], "playwright no instalado"

    url_base = (
        f"{_API}?per_page=50&start_date={desde.isoformat()}&end_date={hasta.isoformat()}"
    )
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            todos: list[dict] = []
            page_num = 1
            total = 9999
            while len(todos) < total and page_num <= 30:
                url = f"{url_base}&page={page_num}"
                page.goto(url, wait_until="networkidle", timeout=90000)
                text = page.inner_text("body")
                data = json.loads(text)
                total = int(data.get("total") or 0)
                batch = data.get("events") or []
                if not batch:
                    break
                todos.extend(batch)
                page_num += 1
            browser.close()
            return todos, None
    except Exception as exc:
        return [], str(exc)


def _cargar_sync_local() -> list[dict]:
    if not _SYNC_FILE.is_file():
        return []
    data = json.loads(_SYNC_FILE.read_text(encoding="utf-8"))
    return data.get("events") or []


def _en_rango(fi: date, ff: date, desde: date, hasta: date) -> bool:
    return not (ff < desde or fi > hasta)


def recolectar_eventos_cordoba_turismo(
    *,
    desde: date,
    hasta: date,
    usar_sync_local: bool = True,
    intentar_api: bool = True,
    intentar_playwright: bool = False,
) -> dict[str, Any]:
    """
    Devuelve eventos mapeados + auditoría (relevantes Bialet vs descartados).
    """
    raw_api: list[dict] = []
    metodo = "ninguno"
    error: str | None = None

    if intentar_api:
        raw_api, error = _fetch_api_paginado(desde, hasta)
        if raw_api:
            metodo = "api_httpx"

    if not raw_api and intentar_playwright:
        raw_api, pw_err = _fetch_playwright(desde, hasta)
        if raw_api:
            metodo = "playwright"
            error = None
        elif pw_err:
            error = pw_err

    if not raw_api and usar_sync_local:
        raw_api = _cargar_sync_local()
        if raw_api:
            metodo = "sync_local"
            error = None

    items: list[dict] = []
    for raw in raw_api:
        row = _tribe_a_item(raw)
        if not row:
            continue
        fi = date.fromisoformat(row["fecha_inicio"])
        ff = date.fromisoformat(row["fecha_fin"])
        if not _en_rango(fi, ff, desde, hasta):
            continue
        items.append(row)

    from ama.engine.evento_relevancia_bialet import enriquecer_angulo_comercial

    relevantes: list[dict] = []
    descartados: list[dict] = []
    for it in items:
        enr = enriquecer_angulo_comercial(it)
        if enr.get("potencial_cabaña"):
            relevantes.append(enr)
        else:
            descartados.append(
                {
                    "nombre": enr.get("nombre"),
                    "fecha_inicio": enr.get("fecha_inicio"),
                    "localidad": enr.get("localidad"),
                    "motivo_filtro": enr.get("motivo_filtro"),
                    "fuente_url": enr.get("fuente_url"),
                }
            )

    auditoria = {
        "actualizado_en": datetime.utcnow().isoformat() + "Z",
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "metodo": metodo,
        "error_api": error,
        "total_bruto": len(items),
        "total_relevantes_bialet": len(relevantes),
        "total_descartados": len(descartados),
        "instrucciones_si_403": (
            "Abrí https://cordobaturismo.gov.ar/agenda/ en Chrome, F12 → Consola, "
            "ejecutá el script en docs/SYNC_CORDOBA_TURISMO.md y guardá el JSON en "
            "ama/data/eventos_cordoba_turismo_sync.json; o: pip install playwright && "
            "playwright install && py -m ama.scrapers.sources_cordoba_turismo --playwright"
        ),
    }

    cache_path = _DATA / "eventos_cordoba_turismo_auditoria.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(
            {**auditoria, "relevantes": relevantes, "descartados_muestra": descartados[:80]},
            f,
            ensure_ascii=False,
            indent=2,
        )

    return {
        "ok": bool(relevantes or items),
        "metodo": metodo,
        "error": error,
        "total_bruto": len(items),
        "total_relevantes": len(relevantes),
        "relevantes": relevantes,
        "auditoria_path": str(cache_path.name),
    }


def main() -> None:
    import argparse

    hoy = date.today()
    anio_marzo = hoy.year + 1 if hoy.month > 3 else hoy.year
    hasta_def = date(anio_marzo, 3, 31)

    ap = argparse.ArgumentParser(description="Sync Córdoba Turismo → Terra Natura")
    ap.add_argument("--desde", default=hoy.isoformat())
    ap.add_argument("--hasta", default=hasta_def.isoformat())
    ap.add_argument("--playwright", action="store_true")
    args = ap.parse_args()

    r = recolectar_eventos_cordoba_turismo(
        desde=date.fromisoformat(args.desde[:10]),
        hasta=date.fromisoformat(args.hasta[:10]),
        intentar_playwright=args.playwright,
    )
    print(
        f"Metodo: {r.get('metodo')} | Bruto: {r.get('total_bruto')} | "
        f"Relevantes Bialet: {r.get('total_relevantes')} | Error: {r.get('error')}"
    )


if __name__ == "__main__":
    main()
