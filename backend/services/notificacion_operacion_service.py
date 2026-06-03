"""
Alertas operativas — reservas Booking, solapes, sync iCal.
Persistencia en config_sistema (clave alertas_operacion).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.services.config_service import get_config, set_config
from backend.services import whatsapp_cloud_service

_CLAVE = "alertas_operacion"
_MAX = 80


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cargar(db: Session) -> list[dict[str, Any]]:
    row = get_config(db, _CLAVE)
    if not row or not isinstance(row.get("valor"), dict):
        return []
    items = row["valor"].get("items")
    return list(items) if isinstance(items, list) else []


def _guardar(db: Session, items: list[dict[str, Any]]) -> None:
    set_config(db, _CLAVE, {"items": items[-_MAX:]}, merge=False)


def registrar_alerta(
    db: Session,
    *,
    tipo: str,
    titulo: str,
    mensaje: str,
    reserva_id: str | None = None,
    unidad_id: str | None = None,
    origen: str | None = None,
    enviar_whatsapp: bool = True,
) -> dict[str, Any]:
    item = {
        "id": str(uuid4()),
        "tipo": tipo,
        "titulo": titulo,
        "mensaje": mensaje,
        "reserva_id": reserva_id,
        "unidad_id": unidad_id,
        "origen": origen,
        "leida": False,
        "creado_en": _ahora_iso(),
    }
    items = _cargar(db)
    items.append(item)
    _guardar(db, items)

    wa = {"ok": False, "skipped": True}
    if enviar_whatsapp:
        wa = whatsapp_cloud_service.notificar_dueno(f"🏡 Terra Natura\n{titulo}\n{mensaje}")
        item["whatsapp_enviado"] = bool(wa.get("ok"))

    return {"alerta": item, "whatsapp": wa}


def listar_alertas(db: Session, *, solo_no_leidas: bool = False, limite: int = 30) -> list[dict]:
    items = _cargar(db)
    if solo_no_leidas:
        items = [i for i in items if not i.get("leida")]
    items.sort(key=lambda x: x.get("creado_en") or "", reverse=True)
    return items[:limite]


def marcar_leidas(db: Session, ids: list[str] | None = None) -> int:
    items = _cargar(db)
    n = 0
    id_set = set(ids) if ids else None
    for i in items:
        if id_set is None or i.get("id") in id_set:
            if not i.get("leida"):
                i["leida"] = True
                n += 1
    _guardar(db, items)
    return n


def notificar_reservas_nuevas(
    db: Session,
    nuevas: list[dict[str, Any]],
    *,
    plataforma: str = "booking",
) -> list[dict]:
    """Crea alertas (y WhatsApp al dueño) por cada reserva importada."""
    creadas: list[dict] = []
    plat = plataforma.capitalize()
    for r in nuevas:
        unidad = r.get("unidad_nombre") or r.get("unidad_id") or "?"
        ci = r.get("check_in") or "?"
        co = r.get("check_out") or "?"
        huesped = r.get("huesped_nombre") or "Huésped"
        titulo = f"Nueva reserva {plat}"
        mensaje = (
            f"{unidad}\n"
            f"Entrada: {ci} · Salida: {co}\n"
            f"{huesped}"
        )
        if r.get("codigo"):
            mensaje += f"\nRef PMS: {r['codigo']}"
        creadas.append(
            registrar_alerta(
                db,
                tipo=f"reserva_{plataforma}",
                titulo=titulo,
                mensaje=mensaje,
                reserva_id=r.get("reserva_id"),
                unidad_id=r.get("unidad_id"),
                origen=plataforma,
            )
        )
    return creadas
