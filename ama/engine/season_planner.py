"""
Sugerencias de publicaciones para el calendario (estacionalidad + feriados).
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from ama.engine.content_strategist import generar_copy

_FERIADOS = Path(__file__).resolve().parent.parent / "data" / "feriados_ar.json"


def _feriados() -> list[dict]:
    if not _FERIADOS.is_file():
        return []
    with _FERIADOS.open(encoding="utf-8") as f:
        return json.load(f)


def sugerir_semana(desde: date | None = None, dias: int = 7) -> list[dict]:
    """Borradores sugeridos (no guardados) para llenar el calendario."""
    start = desde or date.today()
    sugerencias: list[dict] = []
    feriados = {f["fecha"]: f for f in _feriados()}

    angulos_rotacion = ["parejas", "familia", "temporada_baja", "reserva_directa"]
    canales = ["instagram", "facebook", "whatsapp_status"]

    for i in range(dias):
        d = start + timedelta(days=i)
        iso = d.isoformat()
        angulo = angulos_rotacion[i % len(angulos_rotacion)]
        canal = canales[i % len(canales)]
        tema = ""
        if iso in feriados:
            angulo = "evento"
            tema = "feriado_puente"
            cuerpo = f"Puente {feriados[iso]['nombre']} — reservá con anticipación en Bialet Massé."
        elif d.month in (1, 2):
            tema = "verano"
            cuerpo = "Verano en el Valle de Punilla: pileta, parque y cabañas con vista."
        else:
            cuerpo = None

        gen = generar_copy(angulo=angulo, canal=canal, tema_extra=tema, cuerpo_extra=cuerpo)
        sugerencias.append(
            {
                "fecha_publicacion": iso,
                "hora": "10:00" if canal != "whatsapp_status" else "18:00",
                "canal": canal,
                "angulo": angulo,
                "titulo": gen["titulo"],
                "copy": gen["copy"],
                "hashtags": gen["hashtags"],
                "estado_sugerido": "borrador",
                "motivo": f"rotación {angulo}" + (f" · {feriados[iso]['nombre']}" if iso in feriados else ""),
            }
        )
    return sugerencias


def aplicar_sugerencias_a_calendario(desde: date | None = None, dias: int = 7) -> list[dict]:
    from ama.storage.calendar_store import crear_publicacion

    creadas = []
    for s in sugerir_semana(desde, dias):
        row = crear_publicacion(
            {
                "fecha_publicacion": s["fecha_publicacion"],
                "hora": s["hora"],
                "canal": s["canal"],
                "angulo": s["angulo"],
                "titulo": s["titulo"],
                "copy": s["copy"],
                "hashtags": s["hashtags"],
                "estado": "borrador",
                "notas": s.get("motivo", ""),
            }
        )
        creadas.append(row)
    return creadas


def alertas_proximas(dias: int = 60) -> list[dict]:
    """Feriados/puentes en ventana — dispara campañas AMA."""
    hoy = date.today()
    limite = hoy + timedelta(days=dias)
    out: list[dict] = []
    for f in _feriados():
        try:
            fd = date.fromisoformat(f["fecha"])
        except (KeyError, ValueError):
            continue
        if hoy <= fd <= limite:
            delta = (fd - hoy).days
            out.append(
                {
                    "fecha": f["fecha"],
                    "nombre": f.get("nombre", "Feriado"),
                    "dias_restantes": delta,
                    "mensaje": f"En {delta} días: {f.get('nombre', 'feriado')} — armar campaña escapada",
                }
            )
    return sorted(out, key=lambda x: x["dias_restantes"])
