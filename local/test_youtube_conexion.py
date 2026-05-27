"""Prueba rapida: clave .env + API YouTube + BD. Ejecutar: python local/test_youtube_conexion.py"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import httpx
from sqlalchemy import create_engine, text

from backend.config.settings import YOUTUBE_API_KEY, DATABASE_URL
from backend.services.youtube_turismo import buscar_youtube, _api_key_ok, recolectar_videos
from backend.config.database import SessionLocal

def main():
    print("=== 1. Clave en .env ===")
    ok = _api_key_ok()
    print("OK" if ok else "FALTA CLAVE")
    if not ok:
        return 1

    print("\n=== 2. Conexion API (search) ===")
    r = httpx.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "part": "snippet",
            "q": "Bialet Masse turismo",
            "type": "video",
            "maxResults": 2,
            "regionCode": "AR",
            "key": YOUTUBE_API_KEY,
        },
        timeout=25,
    )
    print("HTTP", r.status_code)
    if r.status_code != 200:
        print(r.text[:300])
        return 1
    items = r.json().get("items", [])
    print("Videos:", len(items))
    for it in items:
        print(" -", it["snippet"]["title"][:70])

    print("\n=== 3. buscar_youtube() del proyecto ===")
    vids = buscar_youtube(YOUTUBE_API_KEY, "Cosquin festival turismo", 2)
    print("Resultado:", len(vids))
    if vids:
        print(" -", vids[0]["titulo"][:70])
        print("   url:", vids[0]["url"])

    print("\n=== 4. Base de datos ===")
    db_url = DATABASE_URL.replace("sqlite:///./", "sqlite:///")
    eng = create_engine(db_url)
    with eng.connect() as c:
        n = c.execute(
            text(
                "SELECT COUNT(*) FROM turismo_contenidos "
                "WHERE youtube_id IS NOT NULL AND youtube_id != ''"
            )
        ).scalar()
    print("Videos YouTube guardados:", n)

    print("\n=== 5. Recoleccion (incremental) ===")
    db = SessionLocal()
    try:
        res = recolectar_videos(db)
        print(res)
    finally:
        db.close()

    print("\n=== TODO OK ===")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
