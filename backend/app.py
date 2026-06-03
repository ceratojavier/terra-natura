"""
Terra Natura PMS — API + sitio público y landings
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.config.database import SessionLocal, init_db
from backend.config.settings import API_TITLE, API_VERSION, DEBUG
from backend.routes import (
    agents_routes,
    ama_routes,
    canales_routes,
    config_routes,
    programa_routes,
    public_routes,
    reserva_routes,
    setup_routes,
    turismo_routes,
    unidad_routes,
    video_pro_routes,
    webhook_routes,
)
from backend.services.seed_service import seed_database

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_ROOT = BASE_DIR / "frontend" / "public"
APP_DIST = BASE_DIR / "frontend" / "app" / "dist"
VIDEO_PRO_DIST = BASE_DIR / "frontend" / "video-pro-creator" / "dist"
GUEST_ROOT = BASE_DIR / "guest-app"
ASSETS_DIR = WEB_ROOT / "assets"
MEDIA_DIR = WEB_ROOT / "media"

LANDING_SLUGS = frozenset({"parejas", "familia", "reserva-directa", "punilla"})


def _app_dist_ready() -> bool:
    return (APP_DIST / "index.html").is_file()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_database(db, force=False)
        from backend.services import turismo_service

        turismo_service.seed_database(db, force=False)
    finally:
        db.close()
    yield


app = FastAPI(
    title=API_TITLE,
    description="Gestión configurable + web pública",
    version=API_VERSION,
    debug=DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(unidad_routes.router)
app.include_router(config_routes.router)
app.include_router(reserva_routes.router)
app.include_router(public_routes.router)
app.include_router(canales_routes.router)
app.include_router(ama_routes.router)
app.include_router(programa_routes.router)
app.include_router(agents_routes.router)
app.include_router(turismo_routes.router)
app.include_router(webhook_routes.router)
app.include_router(setup_routes.router)
app.include_router(video_pro_routes.router)

if ASSETS_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

if MEDIA_DIR.is_dir():
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

if GUEST_ROOT.is_dir():
    app.mount("/guia", StaticFiles(directory=str(GUEST_ROOT), html=True), name="guia")


@app.get("/entrar", include_in_schema=False)
async def web_entrada():
    if _app_dist_ready():
        return RedirectResponse(url="/app/hoy", status_code=302)
    return RedirectResponse(url="/programa", status_code=302)


@app.get("/configurador", include_in_schema=False)
async def web_configurador():
    path = WEB_ROOT / "configurador.html"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@app.get("/programa", include_in_schema=False)
async def web_programa():
    if _app_dist_ready():
        return RedirectResponse(url="/app/hoy", status_code=302)
    path = WEB_ROOT / "programa.html"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@app.get("/turismo", include_in_schema=False)
async def web_turismo():
    path = WEB_ROOT / "turismo.html"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@app.get("/agentes", include_in_schema=False)
async def web_agentes():
    if _app_dist_ready():
        return RedirectResponse(url="/app/agentes", status_code=302)
    path = WEB_ROOT / "agentes.html"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@app.get("/marketing", include_in_schema=False)
async def web_marketing():
    if _app_dist_ready():
        return RedirectResponse(url="/app/marketing", status_code=302)
    path = WEB_ROOT / "marketing.html"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@app.get("/panel", include_in_schema=False)
async def web_panel():
    path = WEB_ROOT / "panel.html"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


def _public_html(name: str) -> FileResponse:
    path = WEB_ROOT / f"{name}.html"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@app.get("/reservar", include_in_schema=False)
async def web_reservar():
    return _public_html("reservar")


@app.get("/cabana", include_in_schema=False)
async def web_cabana():
    return _public_html("cabana")


@app.get("/reserva-exito", include_in_schema=False)
async def web_reserva_exito():
    return _public_html("reserva-exito")


@app.get("/reserva-fallo", include_in_schema=False)
async def web_reserva_fallo():
    return _public_html("reserva-fallo")


@app.get("/reserva-pendiente", include_in_schema=False)
async def web_reserva_pendiente():
    return _public_html("reserva-pendiente")


@app.get("/manifest.webmanifest", include_in_schema=False)
async def web_manifest():
    path = WEB_ROOT / "manifest.webmanifest"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="application/manifest+json")


@app.get("/", include_in_schema=False)
async def web_home():
    index = WEB_ROOT / "index.html"
    if not index.is_file():
        return {"mensaje": "Terra Natura PMS", "version": API_VERSION, "docs": "/docs"}
    return FileResponse(index)


@app.get("/landings/{slug}", include_in_schema=False)
async def web_landing(slug: str):
    if slug not in LANDING_SLUGS:
        raise HTTPException(status_code=404)
    path = WEB_ROOT / "landings" / f"{slug}.html"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "version": API_VERSION}


def _register_react_app() -> None:
    """SPA React en /app — fallback a index.html (StaticFiles solo no alcanza /app/programa)."""
    assets_dir = APP_DIST / "assets"
    if assets_dir.is_dir():
        app.mount(
            "/app/assets",
            StaticFiles(directory=str(assets_dir)),
            name="tn-app-assets",
        )

    index = APP_DIST / "index.html"

    @app.get("/app", include_in_schema=False)
    async def spa_app_root():
        return FileResponse(index)

    @app.get("/app/{spa_path:path}", include_in_schema=False)
    async def spa_app_paths(spa_path: str):
        if spa_path.startswith("assets/"):
            raise HTTPException(status_code=404)
        if ".." in spa_path.split("/"):
            raise HTTPException(status_code=400, detail="Ruta inválida")
        candidate = APP_DIST / spa_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index)


if _app_dist_ready():
    _register_react_app()


def _video_pro_ready() -> bool:
    return (VIDEO_PRO_DIST / "index.html").is_file()


def _register_video_pro_app() -> None:
    assets_dir = VIDEO_PRO_DIST / "assets"
    if assets_dir.is_dir():
        app.mount(
            "/video-pro/assets",
            StaticFiles(directory=str(assets_dir)),
            name="video-pro-assets",
        )
    index = VIDEO_PRO_DIST / "index.html"

    @app.get("/video-pro", include_in_schema=False)
    async def spa_video_pro_root():
        return FileResponse(index)

    @app.get("/video-pro/{spa_path:path}", include_in_schema=False)
    async def spa_video_pro_paths(spa_path: str):
        if spa_path.startswith("assets/"):
            raise HTTPException(status_code=404)
        if ".." in spa_path.split("/"):
            raise HTTPException(status_code=400, detail="Ruta inválida")
        candidate = VIDEO_PRO_DIST / spa_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index)


if _video_pro_ready():
    _register_video_pro_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=DEBUG)
