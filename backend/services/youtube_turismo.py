"""
Recolector YouTube Data API v3 — videos reales para grilla turismo.
Requiere YOUTUBE_API_KEY en .env (Google Cloud Console, gratis con cuota diaria).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from backend.config.settings import YOUTUBE_API_KEY
from backend.models.turismo import TurismoContenido

API = "https://www.googleapis.com/youtube/v3"

# Búsquedas orientadas a Bialet, Punilla y Córdoba turismo
QUERIES: list[tuple[str, str]] = [
    ("Bialet Massé turismo qué hacer", "Bialet Massé"),
    ("Bialet Massé Valle de Punilla", "Bialet Massé"),
    ("Labios del Indio Bialet Massé", "Bialet Massé"),
    ("Sendero Buena Vista Bialet Massé", "Bialet Massé"),
    ("Barrancas Bermejas Bialet", "Bialet Massé"),
    ("Festival Cosquín 2026", "Cosquín"),
    ("Festival Nacional Folklore Cosquín", "Cosquín"),
    ("Avicultura Santa María de Punilla", "Santa María de Punilla"),
    ("Villa Carlos Paz turismo lago San Roque", "Villa Carlos Paz"),
    ("Valle de Punilla lugares para visitar", "Valle de Punilla"),
    ("Cosquín turismo", "Cosquín"),
    ("Tanti Córdoba turismo", "Tanti"),
    ("Peatonal cerveza Bialet Massé", "Bialet Massé"),
    ("Carnaval Valle de Punilla", "Valle de Punilla"),
    ("Dique San Roque turismo", "Valle de Punilla"),
    ("Jesús María Córdoba turismo", "Jesús María"),
    ("Córdoba sierras turismo", "Córdoba"),
]

MAX_RESULTS_PER_QUERY = 8
MIN_DURATION_SEC = 30
MAX_DURATION_SEC = 900  # 15 min — reels cortos o tours


def _parse_iso8601_duration(iso: str) -> int:
    """PT1H2M3S → segundos."""
    if not iso or not iso.startswith("PT"):
        return 0
    h = m = s = 0
    for part, mult in ((r"(\d+)H", 3600), (r"(\d+)M", 60), (r"(\d+)S", 1)):
        match = re.search(part, iso)
        if match:
            if mult == 3600:
                h = int(match.group(1))
            elif mult == 60:
                m = int(match.group(1))
            else:
                s = int(match.group(1))
    return h * 3600 + m * 60 + s


def _api_key_ok() -> bool:
    return bool(YOUTUBE_API_KEY and len(YOUTUBE_API_KEY) > 20)


def buscar_youtube(api_key: str, query: str, max_results: int) -> list[dict]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "regionCode": "AR",
        "relevanceLanguage": "es",
        "safeSearch": "moderate",
        "key": api_key,
    }
    with httpx.Client(timeout=30.0) as client:
        r = client.get(f"{API}/search", params=params)
        r.raise_for_status()
        items = r.json().get("items", [])
    ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]
    if not ids:
        return []
    detail_params = {
        "part": "contentDetails,statistics,snippet",
        "id": ",".join(ids),
        "key": api_key,
    }
    with httpx.Client(timeout=30.0) as client:
        r = client.get(f"{API}/videos", params=detail_params)
        r.raise_for_status()
        details = {d["id"]: d for d in r.json().get("items", [])}

    out = []
    for vid in ids:
        d = details.get(vid)
        if not d:
            continue
        dur = _parse_iso8601_duration(d.get("contentDetails", {}).get("duration", ""))
        if dur < MIN_DURATION_SEC or dur > MAX_DURATION_SEC:
            continue
        sn = d.get("snippet", {})
        stats = d.get("statistics", {})
        thumbs = sn.get("thumbnails", {})
        thumb = (
            thumbs.get("high", {}).get("url")
            or thumbs.get("medium", {}).get("url")
            or thumbs.get("default", {}).get("url")
        )
        pub = sn.get("publishedAt")
        publicado = None
        if pub:
            try:
                publicado = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            except ValueError:
                pass
        out.append(
            {
                "youtube_id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "titulo": sn.get("title", "")[:300],
                "canal_autor": sn.get("channelTitle", "")[:200],
                "thumbnail_url": thumb,
                "duracion_segundos": dur,
                "vistas": int(stats.get("viewCount", 0) or 0),
                "publicado_en": publicado,
                "descripcion": (sn.get("description") or "")[:500],
            }
        )
    return out


def recolectar_videos(db: Session, *, max_por_query: int | None = None) -> dict:
    if not _api_key_ok():
        return {
            "ok": False,
            "error": "Falta YOUTUBE_API_KEY en .env — ver docs/YOUTUBE_API_SETUP.md",
            "nuevos": 0,
            "total_youtube": 0,
        }

    max_r = max_por_query or MAX_RESULTS_PER_QUERY
    existentes = {
        r[0]
        for r in db.query(TurismoContenido.youtube_id)
        .filter(TurismoContenido.youtube_id.isnot(None))
        .all()
        if r[0]
    }
    # también por URL
    urls_existentes = {
        row.url
        for row in db.query(TurismoContenido.url).filter(TurismoContenido.plataforma == "youtube").all()
    }

    nuevos = 0
    errores: list[str] = []
    vistos_globales: set[str] = set(existentes)

    for query, localidad in QUERIES:
        try:
            videos = buscar_youtube(YOUTUBE_API_KEY, query, max_r)
        except httpx.HTTPStatusError as e:
            errores.append(f"{query}: HTTP {e.response.status_code}")
            if e.response.status_code == 403:
                errores.append("Cuota agotada o API no habilitada")
                break
            continue
        except Exception as e:
            errores.append(f"{query}: {e}")
            continue

        for v in videos:
            vid = v["youtube_id"]
            if vid in vistos_globales:
                continue
            vistos_globales.add(vid)
            if v["url"] in urls_existentes:
                continue

            notas = f"Búsqueda: {query}"
            if v.get("descripcion"):
                notas += f"\n{v['descripcion'][:400]}"

            row = TurismoContenido(
                plataforma="youtube",
                url=v["url"],
                titulo=v["titulo"],
                canal_autor=v["canal_autor"],
                localidad=localidad,
                notas=notas,
                calidad="alta",
                verificado=True,
                youtube_id=vid,
                thumbnail_url=v["thumbnail_url"],
                duracion_segundos=v["duracion_segundos"],
                vistas=v["vistas"],
                publicado_en=v["publicado_en"],
            )
            db.add(row)
            nuevos += 1
            urls_existentes.add(v["url"])

    db.commit()
    total = (
        db.query(TurismoContenido)
        .filter(TurismoContenido.plataforma == "youtube", TurismoContenido.youtube_id.isnot(None))
        .count()
    )
    return {
        "ok": True,
        "nuevos": nuevos,
        "total_youtube": total,
        "consultas": len(QUERIES),
        "errores": errores,
    }
