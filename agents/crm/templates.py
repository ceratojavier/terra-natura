"""Plantillas comunicación — RQ-17 (antes / durante / después)."""
from __future__ import annotations

from datetime import date

FLUJOS: dict[str, list[dict]] = {
    "consulta": [
        {
            "momento": "consulta",
            "canal": "whatsapp",
            "plantilla": (
                "Hola {nombre}, gracias por escribir a *Cabañas Alpinas Terra Natura* 🏔️\n"
                "Para {check_in} a {check_out} tengo disponibilidad en {unidad}.\n"
                "Total estimado: *${precio} ARS* (seña 50 % para confirmar).\n"
                "¿Te paso link de reserva o preferís transferencia?"
            ),
        }
    ],
    "confirmada": [
        {
            "momento": "confirmacion_pago",
            "canal": "whatsapp",
            "plantilla": (
                "¡Listo {nombre}! Tu reserva está *confirmada* ✅\n"
                "📍 Los Talas 759, Bialet Massé\n"
                "Check-in {check_in} · Check-out {check_out}\n"
                "Te envío políticas y datos de acceso 24 h antes."
            ),
        },
        {
            "momento": "pre_llegada_24h",
            "canal": "whatsapp",
            "plantilla": (
                "Mañana te esperamos en Terra Natura 🌿\n"
                "WiFi y guía local en la cabaña (QR).\n"
                "Cualquier duda, escribinos por acá."
            ),
        },
    ],
    "post_estadia": [
        {
            "momento": "post_checkout_48h",
            "canal": "whatsapp",
            "plantilla": (
                "Gracias por elegirnos, {nombre} 🙌\n"
                "Si te gustó la estadía, nos ayuda mucho tu reseña en Google:\n"
                "{link_resena}\n"
                "¡Te esperamos en la próxima!"
            ),
        },
    ],
}


def sugerir_para_reserva(reserva: dict, config: dict | None = None) -> list[dict]:
    """Devuelve mensajes sugeridos según estado de reserva."""
    estado = reserva.get("estado", "consulta")
    cfg = config or {}
    link = cfg.get("link_resena_google", "https://maps.google.com")

    if estado in ("cerrada", "cancelada"):
        clave = "post_estadia" if estado == "cerrada" else "consulta"
    elif estado in ("confirmada", "checkin_hecho", "ocupada", "checkout_pendiente"):
        clave = "confirmada"
    else:
        clave = "consulta"

    out = []
    for p in FLUJOS.get(clave, FLUJOS["consulta"]):
        texto = p["plantilla"].format(
            nombre=reserva.get("huesped_nombre") or "¿cómo estás?",
            check_in=reserva.get("check_in", ""),
            check_out=reserva.get("check_out", ""),
            unidad=reserva.get("unidad_id", "cabaña"),
            precio=int(reserva.get("precio_total") or 0),
            link_resena=link,
        )
        out.append(
            {
                "momento": p["momento"],
                "canal": p["canal"],
                "texto": texto,
                "estado_reserva": estado,
            }
        )
    return out


def leads_desde_reservas_pendientes(reservas: list[dict]) -> int:
    """Cuenta reservas que necesitan mensaje (pendiente pago / pre llegada)."""
    n = 0
    hoy = date.today().isoformat()
    for r in reservas:
        if r.get("estado") == "pendiente_pago":
            n += 1
        elif r.get("estado") == "confirmada" and r.get("check_in", "") <= hoy:
            n += 1
    return n
