"""
Carga inicial de unidades y configuración.
"""
from sqlalchemy.orm import Session

from backend.data.defaults import CONFIG_DEFAULTS, UNIDADES_INICIALES, config_valor_json
from backend.models.config_sistema import ConfigSistema
from backend.models.unidad import Unidad


def seed_database(db: Session, force: bool = False) -> dict:
    stats = {"unidades": 0, "config": 0}

    for data in UNIDADES_INICIALES:
        uid = data["id"]
        existing = db.get(Unidad, uid)
        if existing and not force:
            continue
        if existing and force:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db.add(Unidad(**data))
        stats["unidades"] += 1

    for clave, (valor, categoria, descripcion) in CONFIG_DEFAULTS.items():
        existing = db.get(ConfigSistema, clave)
        if existing and not force:
            continue
        payload = config_valor_json(valor)
        if existing and force:
            existing.valor = payload
            existing.categoria = categoria
            existing.descripcion = descripcion
        else:
            db.add(
                ConfigSistema(
                    clave=clave,
                    valor=payload,
                    categoria=categoria,
                    descripcion=descripcion,
                )
            )
        stats["config"] += 1

    db.commit()
    return stats
