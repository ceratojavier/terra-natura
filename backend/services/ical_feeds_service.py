"""
Enlaces iCal de importación por unidad y plataforma (Booking, Airbnb, etc.).
"""
from __future__ import annotations

import re
import uuid
from typing import Any

UNIDADES_ICAL: list[dict[str, str]] = [
    {"id": "alpina-1", "nombre": "Alpina 1"},
    {"id": "alpina-2", "nombre": "Alpina 2"},
    {"id": "alpina-3", "nombre": "Alpina 3"},
    {"id": "suite-4", "nombre": "Suite 4 (planta baja)"},
    {"id": "suite-5", "nombre": "Suite 5 (planta alta)"},
]

PLATAFORMAS_ICAL: list[dict[str, str]] = [
    {"id": "booking", "nombre": "Booking.com"},
    {"id": "airbnb", "nombre": "Airbnb"},
    {"id": "vrbo", "nombre": "VRBO / HomeAway"},
    {"id": "otro", "nombre": "Otra plataforma"},
]

# Enlaces export Booking del dueño (mayo 2026) — se usan si feeds_ical está vacío
DEFAULT_FEEDS_BOOKING: list[dict[str, Any]] = [
    {
        "unidad_id": "alpina-1",
        "plataforma": "booking",
        "url": "https://ical.booking.com/v1/export?t=6368e058-74e7-4c34-b05c-53dcf1fc5232",
    },
    {
        "unidad_id": "alpina-2",
        "plataforma": "booking",
        "url": "https://ical.booking.com/v1/export?t=a2a5d9e9-09bd-4b34-a8d4-4926654c0ebf",
    },
    {
        "unidad_id": "alpina-3",
        "plataforma": "booking",
        "url": "https://ical.booking.com/v1/export?t=c67bbf27-9c3d-4995-b54d-c37eaf956754",
    },
    {
        "unidad_id": "suite-4",
        "plataforma": "booking",
        "url": "https://ical.booking.com/v1/export?t=a741cb8f-9675-4a63-ac8d-3c83f3e7b0cc",
    },
    {
        "unidad_id": "suite-5",
        "plataforma": "booking",
        "url": "https://ical.booking.com/v1/export?t=16367ff6-614e-4158-823f-128ef1fa8be8",
    },
]

_URL_RE = re.compile(r"^https?://", re.I)


def _new_feed_id() -> str:
    return f"feed-{uuid.uuid4().hex[:12]}"


def _valid_url(url: str) -> bool:
    u = (url or "").strip()
    return bool(u) and bool(_URL_RE.match(u))


def normalize_feeds(feeds: list[Any] | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for raw in feeds or []:
        if not isinstance(raw, dict):
            continue
        url = str(raw.get("url") or "").strip()
        if not _valid_url(url):
            continue
        plat = str(raw.get("plataforma") or "booking").strip().lower() or "booking"
        if plat not in {p["id"] for p in PLATAFORMAS_ICAL}:
            plat = "otro"
        uid = str(raw.get("unidad_id") or "").strip()
        if uid and uid not in {u["id"] for u in UNIDADES_ICAL}:
            uid = ""
        out.append(
            {
                "id": str(raw.get("id") or _new_feed_id()),
                "unidad_id": uid,
                "plataforma": plat,
                "url": url,
                "notas": str(raw.get("notas") or "").strip()[:200],
            }
        )
    return out


def normalize_canales(valores: dict[str, Any] | None) -> dict[str, Any]:
    """Preferencias + feeds; precarga Booking si no hay feeds."""
    v = dict(valores or {})
    feeds = normalize_feeds(v.get("feeds_ical"))

    if not feeds:
        legacy_b = str(v.get("ical_booking_url") or "").strip()
        legacy_a = str(v.get("ical_airbnb_url") or "").strip()
        if _valid_url(legacy_b):
            feeds.append(
                {
                    "id": _new_feed_id(),
                    "unidad_id": "",
                    "plataforma": "booking",
                    "url": legacy_b,
                    "notas": "Migrado desde campo único",
                }
            )
        if _valid_url(legacy_a):
            feeds.append(
                {
                    "id": _new_feed_id(),
                    "unidad_id": "",
                    "plataforma": "airbnb",
                    "url": legacy_a,
                    "notas": "Migrado desde campo único",
                }
            )

    if not feeds and v.get("booking_habilitado", True) is not False:
        for d in DEFAULT_FEEDS_BOOKING:
            feeds.append({**d, "id": _new_feed_id(), "notas": ""})

    v["feeds_ical"] = feeds
    v.pop("ical_booking_url", None)
    v.pop("ical_airbnb_url", None)
    return v


def resumen_feeds(feeds: list[dict[str, Any]]) -> dict[str, Any]:
    por_unidad: dict[str, list[str]] = {}
    por_plat: dict[str, int] = {}
    for f in feeds:
        plat = f.get("plataforma") or "otro"
        por_plat[plat] = por_plat.get(plat, 0) + 1
        uid = f.get("unidad_id") or "_sin_unidad"
        por_unidad.setdefault(uid, []).append(plat)
    unidades_ok = sum(1 for u in UNIDADES_ICAL if u["id"] in por_unidad)
    return {
        "total": len(feeds),
        "por_plataforma": por_plat,
        "unidades_con_feed": unidades_ok,
        "unidades_total": len(UNIDADES_ICAL),
    }


def check_canales(d: dict[str, Any]) -> dict[str, Any]:
    v = normalize_canales(d)
    feeds = v.get("feeds_ical") or []
    res = resumen_feeds(feeds)
    booking_on = bool(v.get("booking_habilitado", True))
    airbnb_on = bool(v.get("airbnb_habilitado"))

    if not feeds and not booking_on and not airbnb_on:
        return {
            "estado": "parcial",
            "mensaje": "Solo directo — sin iCal de OTAs.",
            "detalle": res,
        }

    if res["unidades_con_feed"] >= 5:
        msg = f"{res['total']} enlace(s) iCal · {res['unidades_con_feed']}/5 unidades cubiertas."
        return {"estado": "ok", "mensaje": msg, "detalle": res}

    if res["total"] >= 1:
        return {
            "estado": "parcial",
            "mensaje": f"{res['total']} enlace(s) — faltan unidades sin iCal ({res['unidades_con_feed']}/5).",
            "detalle": res,
        }

    if "modo_solo_reserva_directa" in v or v.get("booking_habilitado") is not None:
        return {
            "estado": "parcial",
            "mensaje": "Preferencias guardadas — agregá al menos un enlace iCal por unidad.",
            "detalle": res,
        }

    return {
        "estado": "pendiente",
        "mensaje": "Indicá canales y enlaces iCal de exportación.",
        "detalle": res,
    }


def patch_config_canales(canales: dict[str, Any]) -> dict[str, Any]:
    """Payload para config_sistema.clave=config_canales."""
    v = normalize_canales(canales)
    patch: dict[str, Any] = {}
    for key in ("modo_solo_reserva_directa", "booking_habilitado", "airbnb_habilitado"):
        if key in v:
            patch[key] = bool(v[key])
    if v.get("feeds_ical"):
        patch["feeds_ical_import"] = v["feeds_ical"]
    if patch.get("modo_solo_reserva_directa"):
        patch.setdefault("booking_habilitado", False)
        patch.setdefault("airbnb_habilitado", False)
    return patch
