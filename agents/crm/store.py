"""Persistencia leads y mensajes CRM (JSON local MVP)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
LEADS_FILE = DATA / "crm_leads.json"
LOG_FILE = DATA / "crm_mensajes_log.json"


def _load(path: Path, default: list) -> list:
    DATA.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _save(path: Path, data: list) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_leads(estado: str | None = None) -> list[dict]:
    rows = _load(LEADS_FILE, [])
    if estado:
        return [r for r in rows if r.get("estado") == estado]
    return rows


def add_lead(
    nombre: str,
    telefono: str,
    *,
    email: str | None = None,
    origen: str = "whatsapp",
    notas: str = "",
) -> dict:
    rows = _load(LEADS_FILE, [])
    row = {
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "telefono": telefono,
        "email": email,
        "origen": origen,
        "estado": "consulta",
        "notas": notas,
        "creado_en": datetime.now(timezone.utc).isoformat(),
    }
    rows.append(row)
    _save(LEADS_FILE, rows)
    return row


def log_mensaje(lead_id: str, momento: str, canal: str, texto: str) -> dict:
    rows = _load(LOG_FILE, [])
    entry = {
        "id": str(uuid.uuid4()),
        "lead_id": lead_id,
        "momento": momento,
        "canal": canal,
        "texto": texto[:2000],
        "enviado_en": datetime.now(timezone.utc).isoformat(),
    }
    rows.append(entry)
    _save(LOG_FILE, rows)
    return entry
