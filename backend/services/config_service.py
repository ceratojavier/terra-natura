"""
Lectura y actualización de configuración del complejo.
"""
import json
from typing import Any

from sqlalchemy.orm import Session

from backend.models.config_sistema import ConfigSistema


def _parse(valor: str) -> Any:
    try:
        return json.loads(valor)
    except json.JSONDecodeError:
        return valor


def get_config(db: Session, clave: str) -> dict | None:
    row = db.get(ConfigSistema, clave)
    if not row:
        return None
    return {
        "clave": row.clave,
        "valor": _parse(row.valor),
        "categoria": row.categoria,
        "descripcion": row.descripcion,
        "actualizado_en": row.actualizado_en.isoformat() if row.actualizado_en else None,
    }


def list_config(db: Session, categoria: str | None = None) -> list[dict]:
    q = db.query(ConfigSistema)
    if categoria:
        q = q.filter(ConfigSistema.categoria == categoria)
    rows = q.order_by(ConfigSistema.categoria, ConfigSistema.clave).all()
    return [
        {
            "clave": r.clave,
            "valor": _parse(r.valor),
            "categoria": r.categoria,
            "descripcion": r.descripcion,
        }
        for r in rows
    ]


def set_config(db: Session, clave: str, valor: Any, merge: bool = True) -> dict:
    row = db.get(ConfigSistema, clave)
    if row and merge and isinstance(valor, dict):
        current = _parse(row.valor)
        if isinstance(current, dict):
            current.update(valor)
            valor = current
    payload = json.dumps(valor, ensure_ascii=False)
    if row:
        row.valor = payload
    else:
        row = ConfigSistema(clave=clave, valor=payload, categoria="general")
        db.add(row)
    db.commit()
    db.refresh(row)
    return get_config(db, clave)  # type: ignore


def desayuno_habilitado(db: Session) -> bool:
    cfg = get_config(db, "desayuno")
    if not cfg:
        return False
    return bool(cfg["valor"].get("habilitado", False))
