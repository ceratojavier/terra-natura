"""
Piezas editoriales diarias — fidelización, emoción, marca (sin atarse a un evento).
Complementan las campañas por hito en el calendario visual.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

# Lun–Dom: pilar editorial (no venta dura)
_PILAR = {
    0: ("utilidad", "Tip de sierra"),
    1: ("reflexivo_marca", "Marca / refugio"),
    2: ("emocional_tema", "Emoción / fidelizar"),
    3: ("utilidad", "Guía local"),
    4: ("emocional_tema", "Conexión"),
    5: ("reflexivo_marca", "Experiencia"),
    6: ("emocional_tema", "Vínculo"),
}

_TITULOS: dict[str, list[str]] = {
    "emocional_tema": [
        "El río entre las sierras — esa calma que se queda",
        "Atardecer en Bialet sin apuro ni agenda",
        "El sonido del arroyo cuando bajás un cambio",
        "Sierras de Córdoba: el regalo es la pausa",
        "Volvé a respirar — las sierras te esperan",
        "Un mate al borde del agua, sin filtro",
        "Lo que recordás del viaje no es solo la foto",
        "Naturaleza cerca del lago — silencio real",
    ],
    "utilidad": [
        "Tip: 2 noches rinden más que 1 para cortar el estrés",
        "Qué llevar a las sierras en invierno (abrigo + zapatillas)",
        "Plan simple: río a la mañana, pileta a la tarde",
        "Bialet en 48 h — sin correr, sin mapa complicado",
        "Mejor época para ver el lago tranquilo",
    ],
    "reflexivo_marca": [
        "Parque, pileta y dueños en el predio — así es acá",
        "Cabañas alpinas con vista — refugio serrano real",
        "Abrís la ventana y no escuchás ciudad",
        "Terra Natura: naturaleza a 600 m del lago",
        "El predio cuando cae la tarde y prende la pérgola",
    ],
}

_FORMATO_ROT = ("reel", "carousel", "post", "reel", "status", "carousel", "post")


def _titulo(tipo: str, d: date) -> str:
    lista = _TITULOS.get(tipo) or _TITULOS["emocional_tema"]
    return lista[d.toordinal() % len(lista)]


def listar_piezas_editoriales(desde: date, hasta: date) -> list[dict]:
    """Una pieza editorial por día — sin CTA agresivo."""
    out: list[dict] = []
    d = desde
    i = 0
    while d <= hasta:
        tipo, ventana_label = _PILAR.get(d.weekday(), ("emocional_tema", "Editorial"))
        formato = _FORMATO_ROT[i % len(_FORMATO_ROT)]
        if formato == "status":
            canal, formato = "whatsapp", "status"
        else:
            canal = "instagram"

        out.append(
            {
                "pieza_id": f"editorial|{d.isoformat()}",
                "hito_id": "editorial-evergreen",
                "hito_nombre": "Marca y fidelización",
                "tipo_pieza": tipo,
                "titulo": _titulo(tipo, d),
                "fecha": d.isoformat(),
                "fecha_legible": d.strftime("%d/%m/%Y"),
                "ventana_label": ventana_label,
                "tipo_pieza_label": {
                    "emocional_tema": "Emoción / fidelizar",
                    "utilidad": "Tips viajero",
                    "reflexivo_marca": "Marca / refugio",
                }.get(tipo, "Editorial"),
                "estado": "planificada",
                "canal": canal,
                "formato": formato,
                "canal_label": "WhatsApp" if canal == "whatsapp" else "Instagram",
                "formato_label": {"reel": "Reel", "carousel": "Carrusel", "post": "Post", "status": "Status"}.get(
                    formato, formato
                ),
                "color": "#64748b",
                "desarrollado": False,
                "es_editorial": True,
            }
        )
        d += timedelta(days=1)
        i += 1
    return out
