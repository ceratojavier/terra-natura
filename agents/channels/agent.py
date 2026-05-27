"""
Agente CHANNEL MANAGER — calendario único, iCal por unidad, canales OTA/directo.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from agents.core.base import AgentRunResult, AgentStatus, AgentTask, BaseAgent, TaskResult


class ChannelManagerAgent(BaseAgent):
    agent_id = "channels"
    nombre = "Channel Manager"
    descripcion = (
        "Sincroniza ocupación con Airbnb/Booking (iCal), reserva directa web/WhatsApp "
        "y evita overbooking."
    )
    icono = "📅"

    def tareas_disponibles(self) -> list[AgentTask]:
        return [
            AgentTask("estado_canales", "Estado de cada canal y modo solo directo"),
            AgentTask("exportar_ical", "URLs iCal de exportación por unidad"),
            AgentTask("detectar_conflictos", "Solapes y reservas sin ID OTA"),
            AgentTask("ocupacion_7d", "Ocupación próximos 7 días por unidad"),
            AgentTask(
                "sync_ical_import",
                "Importar calendarios Booking/Airbnb al PMS",
            ),
        ]

    def ejecutar(
        self,
        db: Any | None = None,
        *,
        task_ids: list[str] | None = None,
    ) -> AgentRunResult:
        run = self._result_shell(AgentStatus.RUNNING)
        ids = task_ids or [t.id for t in self.tareas_disponibles()]

        if db is None:
            run.status = AgentStatus.ERROR
            run.alertas.append("Sin base de datos — iniciá el servidor PMS")
            run.finalizado = self._now()
            return run

        from backend.models.unidad import Unidad
        from backend.services import disponibilidad_service, reserva_service
        from backend.services.config_service import get_config

        unidades = db.query(Unidad).order_by(Unidad.numero).all()
        cfg_canales = get_config(db, "canales") or get_config(db, "config_canales")
        cfg_val: dict[str, Any] = {}
        modo_directo = False
        if cfg_canales and isinstance(cfg_canales.get("valor"), dict):
            cfg_val = cfg_canales["valor"]
            modo_directo = bool(cfg_val.get("modo_solo_reserva_directa"))
        feeds_import = cfg_val.get("feeds_ical_import") or []

        if "estado_canales" in ids:
            canales = [
                {
                    "id": "web_directa",
                    "nombre": "Web Terra Natura",
                    "activo": True,
                    "sync": "tiempo_real",
                },
                {
                    "id": "whatsapp",
                    "nombre": "WhatsApp",
                    "activo": True,
                    "sync": "manual",
                },
                {
                    "id": "airbnb",
                    "nombre": "Airbnb",
                    "activo": not modo_directo,
                    "sync": "ical_export" if not modo_directo else "pausado",
                },
                {
                    "id": "booking",
                    "nombre": "Booking.com",
                    "activo": not modo_directo,
                    "sync": "ical_export" if not modo_directo else "pausado",
                },
            ]
            run.tareas.append(
                TaskResult(
                    "estado_canales",
                    True,
                    "Solo directo" if modo_directo else "Multicanal (iCal export activo)",
                    {"modo_solo_reserva_directa": modo_directo, "canales": canales},
                )
            )
            if modo_directo:
                run.alertas.append("Modo solo reserva directa: OTAs pausadas en config")

        if "exportar_ical" in ids:
            feeds = [
                {
                    "unidad_id": u.id,
                    "nombre": u.nombre,
                    "url_export": f"/api/unidades/{u.id}/ical",
                    "instruccion": "Importar esta URL en Airbnb/Booking como calendario externo",
                }
                for u in unidades
            ]
            run.tareas.append(
                TaskResult(
                    "exportar_ical",
                    True,
                    f"{len(feeds)} export + {len(feeds_import)} import iCal",
                    {"feeds_export": feeds, "feeds_import": feeds_import},
                )
            )
            if not feeds_import and not modo_directo:
                run.alertas.append(
                    "Configurá enlaces iCal de Booking/Airbnb en /configurador paso Canales"
                )

        if "detectar_conflictos" in ids:
            hoy = date.today()
            hasta = hoy + timedelta(days=365)
            reservas = reserva_service.listar(db, None, hoy, hasta)
            sin_ota = [
                r
                for r in reservas
                if r.get("origen") in ("airbnb", "booking") and not r.get("id_externo_ota")
            ]
            # id_externo not in _to_out - need to extend or query raw
            from backend.models.reserva import Reserva

            rows = (
                db.query(Reserva)
                .filter(Reserva.origen.in_(("airbnb", "booking")))
                .filter(
                    (Reserva.id_externo_ota.is_(None)) | (Reserva.id_externo_ota == "")
                )
                .limit(20)
                .all()
            )
            run.tareas.append(
                TaskResult(
                    "detectar_conflictos",
                    len(rows) == 0,
                    f"{len(rows)} reserva(s) OTA sin ID externo",
                    {"sin_id_externo": len(rows)},
                )
            )
            if rows:
                run.alertas.append("Completá id_externo_ota en reservas de Airbnb/Booking")

        if "sync_ical_import" in ids:
            from backend.services import channel_ical_sync

            sync = channel_ical_sync.sync_todos_los_feeds(db, dry_run=False)
            ok_sync = sync.get("ok", False)
            run.tareas.append(
                TaskResult(
                    "sync_ical_import",
                    ok_sync,
                    sync.get("mensaje")
                    or f"{sync.get('feeds_procesados', 0)} feed(s) procesados",
                    sync,
                )
            )
            if not ok_sync:
                run.alertas.append("Revisá sync iCal — puede haber solapes con reservas directas")

        if "ocupacion_7d" in ids:
            hoy = date.today()
            fin = hoy + timedelta(days=7)
            ocupacion = []
            for u in unidades:
                noches_ocupadas = 0
                d = hoy
                while d < fin:
                    if not disponibilidad_service.estadia_libre(
                        db, u.id, d, d + timedelta(days=1)
                    ):
                        noches_ocupadas += 1
                    d += timedelta(days=1)
                ocupacion.append(
                    {
                        "unidad_id": u.id,
                        "nombre": u.nombre,
                        "noches_ocupadas_7d": noches_ocupadas,
                        "pct": round(100 * noches_ocupadas / 7, 1),
                    }
                )
            run.tareas.append(
                TaskResult(
                    "ocupacion_7d",
                    True,
                    "Mapa 7 días generado",
                    {"unidades": ocupacion},
                )
            )

        run.status = AgentStatus.WARNING if run.alertas else AgentStatus.OK
        run.finalizado = self._now()
        return run
