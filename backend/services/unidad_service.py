"""
Gestión de unidades configurables.
"""
from sqlalchemy.orm import Session

from backend.config.settings import USOS_UNIDAD
from backend.models.unidad import Unidad


def list_unidades(
    db: Session,
    solo_alquilables: bool = False,
    solo_activas: bool = True,
) -> list[dict]:
    q = db.query(Unidad).order_by(Unidad.numero)
    if solo_activas:
        q = q.filter(Unidad.activa.is_(True))
    rows = q.all()
    if solo_alquilables:
        rows = [u for u in rows if u.disponible_para_reserva]
    return [_unidad_to_dict(u) for u in rows]


def get_unidad(db: Session, unidad_id: str) -> dict | None:
    u = db.get(Unidad, unidad_id)
    return _unidad_to_dict(u) if u else None


def update_unidad(db: Session, unidad_id: str, data: dict) -> dict | None:
    u = db.get(Unidad, unidad_id)
    if not u:
        return None

    if "uso_modo" in data and data["uso_modo"] not in USOS_UNIDAD:
        raise ValueError(f"uso_modo inválido. Opciones: {USOS_UNIDAD}")

    # Si pasa a salón / espacio común, dejar de alquilar automáticamente
    if "uso_modo" in data and data["uso_modo"] != "alquiler":
        data.setdefault("alquilable", False)
        data.setdefault("visible_ota", False)

    allowed = {
        "nombre",
        "activa",
        "alquilable",
        "uso_modo",
        "visible_web",
        "visible_ota",
        "capacidad_max",
        "capacidad_recomendada",
        "recomendado_parejas",
        "tiene_aire_acondicionado",
        "color_detalle",
        "precio_verano_min",
        "precio_verano_max",
        "notas_internas",
        "planta",
        "pb_metros_cuadrados",
    }
    for key, value in data.items():
        if key in allowed:
            setattr(u, key, value)

    db.commit()
    db.refresh(u)
    return _unidad_to_dict(u)


def contar_unidades_reservables(db: Session) -> int:
    return len(
        [u for u in db.query(Unidad).filter(Unidad.activa.is_(True)).all() if u.disponible_para_reserva]
    )


def _unidad_to_dict(u: Unidad) -> dict:
    return {
        "id": u.id,
        "nombre": u.nombre,
        "tipo": u.tipo,
        "numero": u.numero,
        "activa": u.activa,
        "alquilable": u.alquilable,
        "uso_modo": u.uso_modo,
        "visible_web": u.visible_web,
        "visible_ota": u.visible_ota,
        "disponible_para_reserva": u.disponible_para_reserva,
        "capacidad_max": u.capacidad_max,
        "capacidad_recomendada": u.capacidad_recomendada,
        "recomendado_parejas": u.recomendado_parejas,
        "planta": u.planta,
        "pb_metros_cuadrados": u.pb_metros_cuadrados,
        "tiene_aire_acondicionado": u.tiene_aire_acondicionado,
        "color_detalle": u.color_detalle,
        "precio_verano_min": u.precio_verano_min,
        "precio_verano_max": u.precio_verano_max,
        "notas_internas": u.notas_internas,
        "slug": u.slug,
    }
