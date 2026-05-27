from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.schemas.config import (
    CanalesUpdate,
    ConfigUpdate,
    DesayunoUpdate,
    Suite4ReglasUpdate,
)
from backend.services import config_service, unidad_service
from backend.services.seed_service import seed_database

router = APIRouter(prefix="/api/config", tags=["Configuración"])


@router.get("")
def listar_config(
    categoria: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return {"config": config_service.list_config(db, categoria=categoria)}


@router.get("/resumen")
def resumen_operativo(db: Session = Depends(get_db)):
    """Vista rápida para el dueño: qué está activo hoy."""
    desayuno = config_service.get_config(db, "desayuno")
    canales = config_service.get_config(db, "canales")
    reservas = config_service.get_config(db, "reservas")
    suite4 = config_service.get_config(db, "suite4_reglas")
    unidades = unidad_service.list_unidades(db, solo_activas=True)
    reservables = [u for u in unidades if u["disponible_para_reserva"]]
    return {
        "unidades_activas": len(unidades),
        "unidades_reservables_hoy": len(reservables),
        "ids_reservables": [u["id"] for u in reservables],
        "desayuno": desayuno["valor"] if desayuno else None,
        "canales": canales["valor"] if canales else None,
        "reservas": reservas["valor"] if reservas else None,
        "suite4_reglas": suite4["valor"] if suite4 else None,
        "unidades": unidades,
    }


@router.get("/{clave}")
def obtener_config(clave: str, db: Session = Depends(get_db)):
    cfg = config_service.get_config(db, clave)
    if not cfg:
        raise HTTPException(404, f"Config '{clave}' no encontrada")
    return cfg


@router.put("/{clave}")
def reemplazar_config(clave: str, body: ConfigUpdate, db: Session = Depends(get_db)):
    return config_service.set_config(db, clave, body.valor, merge=body.merge)


@router.patch("/desayuno")
def configurar_desayuno(body: DesayunoUpdate, db: Session = Depends(get_db)):
    """Activar/desactivar desayuno y parámetros sin tocar JSON manual."""
    patch = body.model_dump(exclude_unset=True)
    if not patch:
        raise HTTPException(400, "Enviá al menos un campo")
    result = config_service.set_config(db, "desayuno", patch, merge=True)

    # Si habilitan desayuno y definen salón, opcionalmente marcar unidad
    if patch.get("habilitado") and patch.get("unidad_salon_id"):
        uid = patch["unidad_salon_id"]
        modo = "salon_desayuno"
        # No forzar automáticamente — el dueño decide; solo documentamos en respuesta
        result["aviso"] = (
            f"Desayuno habilitado. Si querés usar {uid} como salón, "
            f"PATCH /api/unidades/{uid} con uso_modo='{modo}' y alquilable=false"
        )
    return result


@router.patch("/canales")
def configurar_canales(body: CanalesUpdate, db: Session = Depends(get_db)):
    patch = body.model_dump(exclude_unset=True)
    if body.modo_solo_reserva_directa is True:
        patch.setdefault("booking_habilitado", False)
        patch.setdefault("airbnb_habilitado", False)
    return config_service.set_config(db, "canales", patch, merge=True)


@router.patch("/suite4-reglas")
def configurar_suite4(body: Suite4ReglasUpdate, db: Session = Depends(get_db)):
    patch = body.model_dump(exclude_unset=True)
    result = config_service.set_config(db, "suite4_reglas", patch, merge=True)

    if body.modo == "solo_salon":
        from backend.services.unidad_service import update_unidad

        update_unidad(
            db,
            "suite-4",
            {
                "uso_modo": "salon_desayuno",
                "alquilable": False,
                "visible_ota": False,
            },
        )
        result["aviso"] = "Suite 4 pasó a salon_desayuno y dejó de ser alquilable."
    elif body.modo == "independiente":
        from backend.services.unidad_service import update_unidad

        update_unidad(
            db,
            "suite-4",
            {"uso_modo": "alquiler", "alquilable": True, "visible_ota": True},
        )
        result["aviso"] = "Suite 4 restaurada como alquiler independiente."
    return result


@router.post("/seed")
def ejecutar_seed(force: bool = Query(False), db: Session = Depends(get_db)):
    """Carga unidades y config por defecto (solo dev/setup)."""
    return seed_database(db, force=force)
