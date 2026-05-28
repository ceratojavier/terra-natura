from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.unidad import Unidad
from backend.schemas.config import (
    CanalesUpdate,
    ConfigUpdate,
    DesayunoUpdate,
    Suite4ReglasUpdate,
    TarifaOverrideUpsert,
)
from backend.services import config_service, disponibilidad_service, pricing_engine, unidad_service
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


@router.get("/tarifas/calendario")
def calendario_tarifas(
    desde: date = Query(..., description="Inicio YYYY-MM-DD"),
    hasta: date = Query(..., description="Fin YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """
    Calendario tipo Booking: por unidad y por día devuelve
    disponibilidad + precio cotizado de esa noche.
    """
    if hasta < desde:
        raise HTTPException(400, "hasta debe ser >= desde")
    if (hasta - desde).days > 93:
        raise HTTPException(400, "Máximo 93 días por consulta")

    unidades = (
        db.query(Unidad)
        .filter(Unidad.activa.is_(True), Unidad.alquilable.is_(True))
        .order_by(Unidad.numero.asc())
        .all()
    )
    dias: list[date] = []
    cur = desde
    while cur <= hasta:
        dias.append(cur)
        cur += timedelta(days=1)

    data: list[dict] = []
    for u in unidades:
        filas = []
        for d in dias:
            disp = disponibilidad_service.estadia_libre(db, u.id, d, d + timedelta(days=1))
            cot = pricing_engine.cotizar(db, u, d, d + timedelta(days=1))
            n0 = cot.desglose[0] if cot.desglose else None
            filas.append(
                {
                    "fecha": d.isoformat(),
                    "disponible": bool(disp),
                    "precio_noche_ars": round(float(cot.total), 2),
                    "temporada": n0.temporada if n0 else None,
                    "coeficiente_inflacion_pct": n0.coeficiente_inflacion_pct if n0 else None,
                }
            )
        data.append({"unidad_id": u.id, "unidad_nombre": u.nombre, "dias": filas})
    return {"desde": desde.isoformat(), "hasta": hasta.isoformat(), "unidades": data}


@router.post("/tarifas/override")
def guardar_override_tarifa(body: TarifaOverrideUpsert, db: Session = Depends(get_db)):
    """
    Guarda o elimina una tarifa manual por día.
    - precio_noche_ars con valor: guarda override.
    - precio_noche_ars null: elimina override de esa fecha.
    """
    row = config_service.get_config(db, "tarifas_overrides")
    valor = row["valor"] if row and isinstance(row.get("valor"), dict) else {}
    by_unit = valor.get(body.unidad_id) if isinstance(valor.get(body.unidad_id), dict) else {}
    if not isinstance(by_unit, dict):
        by_unit = {}

    if body.precio_noche_ars is None:
        by_unit.pop(body.fecha, None)
    else:
        if body.precio_noche_ars <= 0:
            raise HTTPException(400, "precio_noche_ars debe ser > 0")
        by_unit[body.fecha] = {
            "precio_noche_ars": round(float(body.precio_noche_ars), 2),
            "motivo": body.motivo or "",
        }

    if by_unit:
        valor[body.unidad_id] = by_unit
    else:
        valor.pop(body.unidad_id, None)

    config_service.set_config(db, "tarifas_overrides", valor, merge=False)
    return {"ok": True, "unidad_id": body.unidad_id, "fecha": body.fecha}
