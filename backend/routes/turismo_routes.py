from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services import turismo_service

router = APIRouter(prefix="/api/turismo", tags=["Turismo — grilla y contenidos"])


@router.post("/recolectar")
def recolectar(
    force: bool = Query(False),
    youtube: bool = Query(True),
    db: Session = Depends(get_db),
):
    if force:
        turismo_service.seed_database(db, force=True)
    return turismo_service.recolectar(db, youtube=youtube)


@router.post("/youtube/recolectar")
def youtube_recolectar(db: Session = Depends(get_db)):
    from backend.services.youtube_turismo import recolectar_videos

    return recolectar_videos(db)


@router.get("/grilla")
def grilla(anio: int = Query(2026, ge=2025, le=2030), db: Session = Depends(get_db)):
    from backend.models.turismo import TurismoEvento

    if db.query(TurismoEvento).count() == 0:
        turismo_service.seed_database(db)
    return turismo_service.grilla_anual(db, anio)


@router.get("/grilla/export")
def grilla_export(anio: int = Query(2026), db: Session = Depends(get_db)):
    from backend.models.turismo import TurismoEvento

    if db.query(TurismoEvento).count() == 0:
        turismo_service.seed_database(db)
    path = turismo_service.exportar_grilla(db, anio)
    return FileResponse(path, filename=path.name, media_type="application/json")


@router.get("/eventos")
def listar_eventos(
    localidad: str | None = None,
    mes: int | None = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
):
    from backend.models.turismo import TurismoEvento

    if db.query(TurismoEvento).count() == 0:
        turismo_service.seed_database(db)
    q = db.query(TurismoEvento).filter(TurismoEvento.activo.is_(True))
    if localidad:
        q = q.filter(TurismoEvento.localidad.ilike(f"%{localidad}%"))
    rows = q.all()
    if mes:
        rows = [e for e in rows if turismo_service._evento_en_mes(e, mes, 2026)]
    return {"eventos": [turismo_service._evento_dict(e) for e in rows]}


@router.get("/lugares")
def listar_lugares(db: Session = Depends(get_db)):
    from backend.models.turismo import TurismoLugar

    if db.query(TurismoLugar).count() == 0:
        turismo_service.seed_database(db)
    rows = db.query(TurismoLugar).filter(TurismoLugar.activo.is_(True)).all()
    return {"lugares": [turismo_service._lugar_dict(l) for l in rows]}


@router.get("/contenidos")
def listar_contenidos(
    plataforma: str | None = None,
    solo_youtube_reales: bool = Query(False),
    db: Session = Depends(get_db),
):
    from backend.models.turismo import TurismoContenido

    if db.query(TurismoContenido).count() == 0:
        turismo_service.seed_database(db)
    q = db.query(TurismoContenido)
    if plataforma:
        q = q.filter(TurismoContenido.plataforma == plataforma)
    if solo_youtube_reales:
        q = q.filter(
            TurismoContenido.plataforma == "youtube",
            TurismoContenido.youtube_id.isnot(None),
        )
    rows = q.order_by(TurismoContenido.vistas.desc()).all()
    return {"contenidos": [turismo_service._contenido_dict(c) for c in rows]}
