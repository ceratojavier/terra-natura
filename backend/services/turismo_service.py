"""
Servicio base de datos turismo — seed, grilla anual, exportación.
"""
from __future__ import annotations

import json
from calendar import month_name
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from backend.models.turismo import TurismoContenido, TurismoEvento, TurismoLugar
from backend.services import turismo_seed_data as seed

REPO = Path(__file__).resolve().parent.parent.parent
EXPORT_DIR = REPO / "agents" / "data" / "turismo"


def _normalizar_evento_row(row: dict) -> dict:
    for key in ("fecha_inicio", "fecha_fin"):
        if key in row and isinstance(row[key], str):
            row[key] = date.fromisoformat(row[key])
    return row


def seed_database(db: Session, *, force: bool = False) -> dict:
    if force:
        db.query(TurismoContenido).delete()
        db.query(TurismoEvento).delete()
        db.query(TurismoLugar).delete()
        db.commit()
    elif db.query(TurismoEvento).count() > 0:
        return {"ok": True, "mensaje": "Ya hay datos — usá force=true para recargar", "eventos": db.query(TurismoEvento).count()}

    lugar_map: dict[str, str] = {}
    for row in seed.LUGARES:
        o = TurismoLugar(**row)
        db.add(o)
        db.flush()
        lugar_map[row["nombre"]] = o.id

    evento_map: dict[str, str] = {}
    for row in seed.EVENTOS:
        data = _normalizar_evento_row(dict(row))
        o = TurismoEvento(**data)
        db.add(o)
        db.flush()
        evento_map[row["nombre"]] = o.id

    for row in seed.CONTENIDOS:
        data = dict(row)
        ev_name = data.pop("evento_nombre", None)
        lug_name = data.pop("lugar_nombre", None)
        if ev_name and ev_name in evento_map:
            data["evento_id"] = evento_map[ev_name]
        if lug_name and lug_name in lugar_map:
            data["lugar_id"] = lugar_map[lug_name]
        db.add(TurismoContenido(**data))

    db.commit()
    return {
        "ok": True,
        "lugares": len(seed.LUGARES),
        "eventos": len(seed.EVENTOS),
        "contenidos": len(seed.CONTENIDOS),
    }


def _evento_en_mes(ev: TurismoEvento, mes: int, anio: int) -> bool:
    if ev.fecha_inicio and ev.fecha_fin:
        if ev.fecha_inicio.year == anio or ev.fecha_fin.year == anio:
            if ev.fecha_inicio.month <= mes <= ev.fecha_fin.month:
                return True
            if ev.fecha_inicio.month <= mes and ev.fecha_fin.month >= mes:
                return True
        if ev.fecha_inicio.month == mes or ev.fecha_fin.month == mes:
            return True
    if ev.mes_inicio and ev.mes_fin:
        if ev.mes_inicio <= ev.mes_fin:
            return ev.mes_inicio <= mes <= ev.mes_fin
        return mes >= ev.mes_inicio or mes <= ev.mes_fin
    if ev.mes_inicio:
        return ev.mes_inicio == mes
    return False


def grilla_anual(db: Session, anio: int = 2026) -> dict:
    eventos = (
        db.query(TurismoEvento)
        .filter(TurismoEvento.activo.is_(True))
        .order_by(TurismoEvento.prioridad, TurismoEvento.localidad)
        .all()
    )
    lugares = (
        db.query(TurismoLugar)
        .filter(TurismoLugar.activo.is_(True))
        .order_by(TurismoLugar.localidad, TurismoLugar.nombre)
        .all()
    )
    contenidos = db.query(TurismoContenido).order_by(TurismoContenido.plataforma).all()

    meses: list[dict] = []
    for m in range(1, 13):
        nombre_mes = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
        ][m - 1]
        ev_mes = [e for e in eventos if _evento_en_mes(e, m, anio)]
        meses.append(
            {
                "mes": m,
                "nombre": nombre_mes,
                "eventos": [_evento_dict(e) for e in ev_mes],
                "total": len(ev_mes),
            }
        )

    return {
        "anio": anio,
        "generado": date.today().isoformat(),
        "resumen": {
            "lugares": len(lugares),
            "eventos": len(eventos),
            "contenidos": len(contenidos),
            "por_plataforma": _count_plataforma(contenidos),
        },
        "meses": meses,
        "lugares_todo_anio": [_lugar_dict(l) for l in lugares],
        "banco_contenidos": [_contenido_dict(c) for c in contenidos],
    }


def exportar_grilla(db: Session, anio: int = 2026) -> Path:
    data = grilla_anual(db, anio)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORT_DIR / f"grilla_anual_{anio}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def recolectar(db: Session, *, youtube: bool = True) -> dict:
    """Carga seed + exporta grilla + opcional YouTube API."""
    r = seed_database(db, force=False)
    path = exportar_grilla(db)
    out = {"seed": r, "grilla_export": str(path)}
    if youtube:
        from backend.services.youtube_turismo import recolectar_videos

        out["youtube"] = recolectar_videos(db)
    return out


def _evento_dict(e: TurismoEvento) -> dict:
    return {
        "id": e.id,
        "nombre": e.nombre,
        "localidad": e.localidad,
        "categoria": e.categoria,
        "fecha_inicio": e.fecha_inicio.isoformat() if e.fecha_inicio else None,
        "fecha_fin": e.fecha_fin.isoformat() if e.fecha_fin else None,
        "mes_inicio": e.mes_inicio,
        "dia_aprox": e.dia_aprox,
        "descripcion": e.descripcion,
        "distancia_km_bialet": e.distancia_km_bialet,
        "entrada": e.entrada,
        "tags": e.tags,
        "prioridad": e.prioridad,
        "fuente_url": e.fuente_url,
        "apto_video": e.apto_video,
    }


def _lugar_dict(l: TurismoLugar) -> dict:
    return {
        "id": l.id,
        "nombre": l.nombre,
        "localidad": l.localidad,
        "categoria": l.categoria,
        "descripcion": l.descripcion,
        "distancia_km_bialet": l.distancia_km_bialet,
        "tags": l.tags,
        "fuente_url": l.fuente_url,
    }


def _contenido_dict(c: TurismoContenido) -> dict:
    return {
        "id": c.id,
        "plataforma": c.plataforma,
        "url": c.url,
        "titulo": c.titulo,
        "localidad": c.localidad,
        "calidad": c.calidad,
        "verificado": c.verificado,
        "notas": c.notas,
        "youtube_id": c.youtube_id,
        "thumbnail_url": c.thumbnail_url,
        "duracion_segundos": c.duracion_segundos,
        "vistas": c.vistas,
        "publicado_en": c.publicado_en.isoformat() if c.publicado_en else None,
        "canal_autor": c.canal_autor,
    }


def _count_plataforma(contenidos: list[TurismoContenido]) -> dict[str, int]:
    out: dict[str, int] = {}
    for c in contenidos:
        out[c.plataforma] = out.get(c.plataforma, 0) + 1
    return out
