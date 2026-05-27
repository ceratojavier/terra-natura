"""
Descarga automática de imágenes para festivales / recitales / eventos.
Fuentes (en orden): página oficial (og:image) → Wikimedia Commons.
Guarda en archivos multimedia/fotos terra natura/FESTIVALES/
"""
from __future__ import annotations

import json
import re
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin, urlparse

import httpx

_REPO = Path(__file__).resolve().parent.parent.parent
_DATA = Path(__file__).resolve().parent.parent / "data"
_FOTOS = _REPO / "archivos multimedia" / "fotos terra natura"
_FESTIVALES = _FOTOS / "FESTIVALES"
_CACHE = _DATA / "eventos_imagenes_cache.json"
_CREDITOS = _FESTIVALES / "CREDITOS_DESCARGA_WEB.txt"

UA = "TerraNatura-AMA/1.0 (uso local marketing; Bialet Masse)"

_OG_PATTERNS = [
    re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', re.I),
    re.compile(r'<meta[^>]+property=["\']og:image:secure_url["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)', re.I),
]

_CATEGORIAS_DESCARGA = frozenset(
    {"festival", "fiesta", "electronica", "musica", "deporte", "gastronomia", "feria", "carnaval"}
)


def _load_cache() -> dict:
    if not _CACHE.is_file():
        return {"intentos": {}, "archivos": {}}
    with _CACHE.open(encoding="utf-8") as f:
        return json.load(f)


def _save_cache(c: dict) -> None:
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    with _CACHE.open("w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)


def _clave_evento(ev: dict) -> str:
    return f"{ev.get('nombre','')}|{ev.get('fecha_inicio','')}|{ev.get('localidad','')}"


def _slug(nombre: str) -> str:
    s = nombre.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")[:80] or "evento"


def _necesita_imagen_web(ev: dict) -> bool:
    from ama.engine.evento_post_preview import _foto_evento, _match_festival

    tipo = ev.get("tipo") or ""
    cat = (ev.get("categoria") or "").lower()
    nombre = (ev.get("nombre") or "").lower()

    if tipo in ("feriado_nacional", "finde_largo", "vacaciones_invierno", "promo_invierno", "referencia"):
        return False
    if cat and cat not in _CATEGORIAS_DESCARGA:
        if not any(
            k in nombre
            for k in (
                "festival",
                "fiesta",
                "recital",
                "carnaval",
                "oktober",
                "cosquin",
                "kempes",
                "feria",
                "electron",
                "estacion",
            )
        ):
            return False

    rel_fest = _match_festival(ev.get("nombre") or "", ev.get("localidad") or "")
    if rel_fest:
        return False

    _url, origen, real = _foto_evento(ev)
    if origen == "fotos/FESTIVALES":
        return False
    return True


def _candidatos_imagen_html(html: str, base_url: str) -> list[str]:
    vistos: set[str] = set()
    out: list[str] = []

    def add(u: str, prio: bool = False) -> None:
        u = u.strip()
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/"):
            u = urljoin(base_url, u)
        if not u.startswith("http") or u in vistos:
            return
        low = u.lower()
        if any(x in low for x in ("logo", "icon", "favicon", "sprite", "avatar", "1x1", "pixel", ".svg")):
            return
        vistos.add(u)
        if prio:
            out.insert(0, u)
        else:
            out.append(u)

    for pat in _OG_PATTERNS:
        m = pat.search(html)
        if m:
            add(m.group(1), prio=True)

    for m in re.finditer(
        r'(?:src|href)=["\']([^"\']+\.(?:jpg|jpeg|png|webp)(?:\?[^"\']*)?)["\']',
        html[:250_000],
        re.I,
    ):
        u = m.group(1)
        add(u, prio="wp-content/uploads" in u.lower() or "2024" in u or "2025" in u or "2026" in u)

    return out


def _url_imagen_viva(url: str, client: httpx.Client, referer: str) -> bool:
    try:
        headers = {"Referer": referer} if referer else {}
        with client.stream("GET", url, timeout=20, headers=headers, follow_redirects=True) as r:
            if r.status_code != 200:
                return False
            ct = (r.headers.get("content-type") or "").lower()
            if "image" not in ct and not url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                return False
            chunk = b""
            for part in r.iter_bytes(8192):
                chunk += part
                if len(chunk) > 4000:
                    return True
            return len(chunk) > 3000
    except Exception:
        return False


def _buscar_og_en_url(url: str, client: httpx.Client) -> str | None:
    try:
        r = client.get(url, timeout=25)
        r.raise_for_status()
        if "image" in (r.headers.get("content-type") or "").lower():
            return str(r.url)
        for cand in _candidatos_imagen_html(r.text[:400_000], str(r.url)):
            if _url_imagen_viva(cand, client, url):
                return cand
        return None
    except Exception:
        return None


def _wikimedia_imagen(query: str, client: httpx.Client) -> tuple[str | None, str | None]:
    """Devuelve (url_imagen, titulo_commons)."""
    api = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": 5,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 1400,
        "format": "json",
    }
    try:
        r = client.get(api, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages") or {}
        for page in sorted(pages.values(), key=lambda p: p.get("index", 99)):
            ii = (page.get("imageinfo") or [{}])[0]
            url = ii.get("thumburl") or ii.get("url")
            if url and "svg" not in url.lower():
                title = page.get("title", "")
                return url, title
    except Exception:
        pass
    return None, None


def _descargar_bytes(url: str, dest: Path, client: httpx.Client, referer: str = "") -> bool:
    try:
        headers = {}
        if referer:
            headers["Referer"] = referer
        r = client.get(url, timeout=60, headers=headers)
        r.raise_for_status()
        ct = (r.headers.get("content-type") or "").lower()
        if "image" not in ct and not url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return False
        if len(r.content) < 3000:
            return False
        if "webp" in ct or url.lower().endswith(".webp"):
            dest = dest.with_suffix(".webp")
        elif "png" in ct:
            dest = dest.with_suffix(".png")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        return dest.is_file() and dest.stat().st_size > 3000
    except Exception:
        return False


def _append_credito(linea: str) -> None:
    _FESTIVALES.mkdir(parents=True, exist_ok=True)
    prev = _CREDITOS.read_text(encoding="utf-8") if _CREDITOS.is_file() else ""
    if linea in prev:
        return
    with _CREDITOS.open("a", encoding="utf-8") as f:
        f.write(linea + "\n")


def descargar_foto_evento(ev: dict, *, client: httpx.Client | None = None) -> dict[str, Any]:
    """
    Intenta bajar una imagen del evento. No inventa: solo og:image o Commons.
    """
    cache = _load_cache()
    clave = _clave_evento(ev)
    intentos = cache.setdefault("intentos", {})
    if intentos.get(clave, {}).get("ok"):
        arch = cache.get("archivos", {}).get(clave)
        if arch:
            return {"ok": True, "rel_path": arch, "fuente": "cache", "mensaje": "Ya descargada"}

    hoy = date.today().isoformat()
    if (
        intentos.get(clave, {}).get("fecha") == hoy
        and not intentos.get(clave, {}).get("ok")
        and not ev.get("_forzar_descarga")
    ):
        return {"ok": False, "mensaje": "Ya se intentó hoy sin resultado"}

    nombre = ev.get("nombre") or "evento"
    localidad = ev.get("localidad") or ""
    fuente_url = ev.get("fuente_url") or ev.get("fuente") or ""

    own_client = client is None
    if own_client:
        client = httpx.Client(
            headers={"User-Agent": UA},
            follow_redirects=True,
        )

    img_url: str | None = None
    credito = ""
    origen = ""

    try:
        if fuente_url.startswith("http"):
            img_url = _buscar_og_en_url(fuente_url, client)
            if img_url:
                origen = "og:image"
                credito = f"{nombre}: og:image de {fuente_url}"

        if not img_url:
            for q in (
                f"{nombre} {localidad}",
                f"{nombre} Argentina festival",
                f"{localidad} Cordoba Argentina",
            ):
                img_url, commons_title = _wikimedia_imagen(q, client)
                if img_url:
                    break
            else:
                commons_title = None
            if img_url:
                origen = "wikimedia_commons"
                credito = f"{nombre}: {commons_title} — Wikimedia Commons"

        if not img_url:
            intentos[clave] = {"fecha": hoy, "ok": False, "error": "sin_imagen_en_web"}
            _save_cache(cache)
            return {"ok": False, "mensaje": "No se encontró imagen pública para este evento"}

        ext = ".jpg"
        path_url = urlparse(img_url).path.lower()
        if ".png" in path_url:
            ext = ".png"
        elif ".webp" in path_url:
            ext = ".webp"

        fname = f"FESTIVALES_{_slug(nombre)}{ext}"
        dest = _FESTIVALES / fname
        if dest.is_file() and dest.stat().st_size > 8000:
            rel = dest.relative_to(_FOTOS).as_posix()
            cache.setdefault("archivos", {})[clave] = rel
            intentos[clave] = {"fecha": hoy, "ok": True, "origen": "existente"}
            _save_cache(cache)
            return {"ok": True, "rel_path": rel, "fuente": "disco"}

        if not _descargar_bytes(img_url, dest, client, referer=fuente_url if fuente_url.startswith("http") else ""):
            intentos[clave] = {"fecha": hoy, "ok": False, "error": "descarga_fallida"}
            _save_cache(cache)
            return {"ok": False, "mensaje": "La URL de imagen no respondió"}

        rel = dest.relative_to(_FOTOS).as_posix()
        cache.setdefault("archivos", {})[clave] = rel
        intentos[clave] = {"fecha": hoy, "ok": True, "origen": origen, "url": img_url}
        _save_cache(cache)
        _append_credito(f"{credito}\n  Archivo: {rel}\n  URL: {img_url}\n  ---")
        return {
            "ok": True,
            "rel_path": rel,
            "fuente": origen,
            "url": img_url,
            "mensaje": f"Imagen guardada ({origen})",
        }
    finally:
        if own_client and client:
            client.close()


def descargar_fotos_faltantes(
    eventos: list[dict],
    *,
    max_descargas: int = 12,
    pausa_seg: float = 2.0,
) -> dict[str, Any]:
    """Procesa lista de eventos; descarga hasta max_descargas imágenes nuevas."""
    candidatos = [ev for ev in eventos if _necesita_imagen_web(ev)]
    ok = fail = skip = 0
    detalle: list[dict] = []

    with httpx.Client(headers={"User-Agent": UA}, follow_redirects=True) as client:
        for ev in candidatos:
            if ok >= max_descargas:
                break
            if not _necesita_imagen_web(ev):
                skip += 1
                continue
            time.sleep(pausa_seg)
            r = descargar_foto_evento(ev, client=client)
            row = {"nombre": ev.get("nombre"), "ok": r.get("ok"), "mensaje": r.get("mensaje"), "rel_path": r.get("rel_path")}
            detalle.append(row)
            if r.get("ok"):
                ok += 1
            else:
                fail += 1

    return {
        "ok": True,
        "candidatos": len(candidatos),
        "descargadas": ok,
        "fallidas": fail,
        "omitidas": skip,
        "detalle": detalle[:20],
        "mensaje": f"Fotos web: {ok} nuevas, {fail} sin resultado (de {len(candidatos)} eventos sin banner propio).",
    }


def descargar_desde_confirmados_y_cache(
    *,
    desde: date | None = None,
    hasta: date | None = None,
    max_descargas: int = 15,
) -> dict[str, Any]:
    """Usa eventos confirmados + cache de agenda."""
    hoy = desde or date.today()
    if hasta is None:
        anio = hoy.year + 1 if hoy.month > 3 else hoy.year
        hasta = date(anio, 3, 31)

    eventos: list[dict] = []
    conf = _load_cache()
    confirmados_path = _DATA / "eventos_confirmados_ar.json"
    if confirmados_path.is_file():
        with confirmados_path.open(encoding="utf-8") as f:
            for ev in json.load(f).get("eventos", []):
                fi = ev.get("fecha_inicio")
                if not fi:
                    continue
                try:
                    d_ini = date.fromisoformat(fi[:10])
                    d_fin = date.fromisoformat((ev.get("fecha_fin") or fi)[:10])
                except ValueError:
                    continue
                if d_fin >= hoy and d_ini <= hasta:
                    eventos.append(ev)

    from ama.scrapers.event_hunter import leer_cache

    for ev in leer_cache().get("items", []):
        if ev.get("estado") == "confirmado" or ev.get("tipo") == "evento_confirmado":
            eventos.append(ev)

    return descargar_fotos_faltantes(eventos, max_descargas=max_descargas)


if __name__ == "__main__":
    from datetime import date

    r = descargar_desde_confirmados_y_cache(desde=date.today())
    print(r.get("mensaje", r))
    for d in r.get("detalle") or []:
        print(" ", "OK" if d.get("ok") else "—", d.get("nombre"), d.get("mensaje", ""))
