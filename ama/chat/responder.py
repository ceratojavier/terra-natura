"""
Respuestas consultas (WhatsApp / web futuro).
MVP: reglas + llamadas al PMS (disponibilidad/cotización) cuando exista sesión DB.
Integración LLM opcional con OPENAI_API_KEY (no obligatoria).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RespuestaBorrador:
    texto: str
    debe_escalar_humano: bool
    motivo_escalado: str | None = None


def responder_consulta_texto_plano(mensaje: str) -> RespuestaBorrador:
    """
    Placeholder inteligencia de negocio: detecta palabras clave y sugiere respuesta.
    Cuando haya API WhatsApp, el webhook llamará al PMS y armará el texto final.
    """
    m = (mensaje or "").lower().strip()
    if any(x in m for x in ("reclamo", "queja", "devolución", "denuncia")):
        return RespuestaBorrador(
            texto=(
                "Te derivo con el equipo del complejo para que te ayuden personalmente. "
                "Escribinos por el mismo número en horario habitual."
            ),
            debe_escalar_humano=True,
            motivo_escalado="posible_reclamo",
        )
    if any(x in m for x in ("disponibilidad", "precio", "cuánto", "reserva", "fecha")):
        return RespuestaBorrador(
            texto=(
                "Para fechas y valores exactos usamos el calendario del complejo. "
                "Pasame unidad deseada y check-in / check-out y te cotizo (o entrá a la web "
                "que tiene cotización orientativa)."
            ),
            debe_escalar_humano=False,
        )
    return RespuestaBorrador(
        texto=(
            "Hola, gracias por escribir a Cabañas Alpinas Terra Natura. "
            "Contame fechas y qué unidad te interesa y te ayudamos."
        ),
        debe_escalar_humano=False,
    )
