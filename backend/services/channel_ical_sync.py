"""
Importación iCal desde Booking/Airbnb → reservas bloqueantes en el PMS.
Un calendario único: la web cotiza contra la misma ocupación que las OTAs.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any

import httpx
from sqlalchemy.orm import Session

from backend.models.reserva import Reserva
from backend.services import disponibilidad_service, ical_feeds_service
from backend.services.config_service import get_config

_DATE_RE = re.compile(r"^(\d{8})")
_UID_DOMAIN = "@pms.terra-natura.local"


def _unfold_lines(text: str) -> list[str]:
    raw = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    for line in raw:
        if line.startswith((" ", "\t")) and out:
            out[-1] += line[1:].strip()
        elif line.strip():
            out.append(line.strip())
    return out


def _parse_ical_date(value: str) -> date | None:
    v = (value or "").strip()
    if not v:
        return None
    if "T" in v:
        v = v.split("T", 1)[0]
    m = _DATE_RE.match(v.replace("-", "")[:8])
    if not m:
        return None
    s = m.group(1)
    try:
        return date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
    except ValueError:
        return None


def _prop_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        return line.upper(), ""
    head, val = line.split(":", 1)
    key = head.split(";", 1)[0].upper()
    return key, val.strip()


def parse_ical_events(ics_text: str) -> list[dict[str, Any]]:
    """Extrae VEVENT con DTSTART/DTEND DATE (fin exclusivo, igual que export PMS)."""
    lines = _unfold_lines(ics_text)
    events: list[dict[str, Any]] = []
    in_event = False
    cur: dict[str, Any] = {}

    for line in lines:
        if line == "BEGIN:VEVENT":
            in_event = True
            cur = {}
            continue
        if line == "END:VEVENT":
            if in_event and cur.get("uid") and cur.get("check_in") and cur.get("check_out"):
                if cur["check_out"] > cur["check_in"]:
                    events.append(cur)
            in_event = False
            cur = {}
            continue
        if not in_event:
            continue
        key, val = _prop_value(line)
        if key == "UID":
            cur["uid"] = val.split(_UID_DOMAIN, 1)[0].strip()
        elif key == "DTSTART":
            d = _parse_ical_date(val)
            if d:
                cur["check_in"] = d
        elif key == "DTEND":
            d = _parse_ical_date(val)
            if d:
                cur["check_out"] = d
        elif key == "SUMMARY":
            cur["summary"] = val[:160]

    return events


def _feeds_desde_config(db: Session) -> list[dict[str, Any]]:
    for clave in ("config_canales", "canales"):
        row = get_config(db, clave)
        if not row or not isinstance(row.get("valor"), dict):
            continue
        v = ical_feeds_service.normalize_canales(row["valor"])
        feeds = v.get("feeds_ical") or row["valor"].get("feeds_ical_import") or []
        if feeds:
            return ical_feeds_service.normalize_feeds(feeds)
    return ical_feeds_service.normalize_feeds(ical_feeds_service.DEFAULT_FEEDS_BOOKING)


def _origen_desde_plataforma(plataforma: str) -> str:
    p = (plataforma or "booking").lower()
    if p == "airbnb":
        return "airbnb"
    if p == "booking":
        return "booking"
    return "otro"


def _buscar_por_uid(db: Session, unidad_id: str, uid: str) -> Reserva | None:
    return (
        db.query(Reserva)
        .filter(
            Reserva.unidad_id == unidad_id,
            Reserva.id_externo_ota == uid,
        )
        .first()
    )


def sync_feed(
    db: Session,
    *,
    unidad_id: str,
    url: str,
    plataforma: str = "booking",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Importa un feed iCal a reservas confirmadas bloqueantes."""
    if not unidad_id:
        return {"ok": False, "error": "unidad_id requerido", "creadas": 0, "actualizadas": 0}

    try:
        with httpx.Client(timeout=45.0, follow_redirects=True) as client:
            r = client.get(url, headers={"User-Agent": "TerraNatura-PMS/1.0"})
            r.raise_for_status()
            ics = r.text
    except Exception as e:
        return {"ok": False, "error": str(e), "creadas": 0, "actualizadas": 0}

    eventos = parse_ical_events(ics)
    origen = _origen_desde_plataforma(plataforma)
    creadas = actualizadas = omitidas = 0
    errores: list[str] = []

    for ev in eventos:
        uid = str(ev["uid"])
        ci: date = ev["check_in"]
        co: date = ev["check_out"]
        existente = _buscar_por_uid(db, unidad_id, uid)

        if existente:
            if existente.check_in != ci or existente.check_out != co:
                if dry_run:
                    actualizadas += 1
                else:
                    if disponibilidad_service.estadia_libre(
                        db, unidad_id, ci, co, exclude_reserva_id=existente.id
                    ):
                        existente.check_in = ci
                        existente.check_out = co
                        existente.actualizado_en = datetime.now(timezone.utc)
                        actualizadas += 1
                    else:
                        errores.append(f"Solape al actualizar {uid}")
            else:
                omitidas += 1
            continue

        if not disponibilidad_service.estadia_libre(db, unidad_id, ci, co):
            errores.append(f"Sin lugar {ci}–{co} ({uid[:20]}…)")
            continue

        if dry_run:
            creadas += 1
            continue

        nombre = ev.get("summary") or f"Import {plataforma}"
        r = Reserva(
            unidad_id=unidad_id,
            check_in=ci,
            check_out=co,
            estado="confirmada",
            origen=origen,
            huesped_nombre=nombre[:160],
            personas=2,
            precio_total=0.0,
            id_externo_ota=uid,
            notas_internas=f"Sync iCal {plataforma} {datetime.now(timezone.utc).isoformat()}",
        )
        db.add(r)
        db.flush()
        creadas += 1

    if not dry_run and (creadas or actualizadas):
        db.commit()

    return {
        "ok": len(errores) == 0,
        "unidad_id": unidad_id,
        "plataforma": plataforma,
        "eventos": len(eventos),
        "creadas": creadas,
        "actualizadas": actualizadas,
        "omitidas": omitidas,
        "errores": errores[:15],
    }


def sync_todos_los_feeds(db: Session, *, dry_run: bool = False) -> dict[str, Any]:
    """Sincroniza todos los feeds configurados (o defaults Booking por unidad)."""
    cfg_row = get_config(db, "config_canales") or get_config(db, "canales")
    modo_directo = False
    if cfg_row and isinstance(cfg_row.get("valor"), dict):
        modo_directo = bool(cfg_row["valor"].get("modo_solo_reserva_directa"))

    if modo_directo:
        return {
            "ok": True,
            "mensaje": "Modo solo reserva directa — import OTA omitido",
            "feeds": [],
        }

    feeds = _feeds_desde_config(db)
    resultados: list[dict] = []
    for f in feeds:
        uid = f.get("unidad_id") or ""
        url = f.get("url") or ""
        if not uid or not url:
            continue
        resultados.append(
            sync_feed(
                db,
                unidad_id=uid,
                url=url,
                plataforma=str(f.get("plataforma") or "booking"),
                dry_run=dry_run,
            )
        )

    ok = all(r.get("ok", False) for r in resultados) if resultados else True
    return {
        "ok": ok,
        "feeds_procesados": len(resultados),
        "detalle": resultados,
        "sync_en": datetime.now(timezone.utc).isoformat(),
    }
