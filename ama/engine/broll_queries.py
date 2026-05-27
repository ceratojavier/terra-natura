"""Consultas YouTube B-roll por tipo de escena — biblioteca de recursos."""

# tipo_escena -> búsqueda API YouTube
BROLL_POR_TIPO: dict[str, str] = {
    "rio_agua": "rio arroyo agua sierras Cordoba Argentina",
    "lago": "lago San Roque Cordoba drone atardecer",
    "sierras": "sierras Cordoba atardecer naturaleza",
    "bialet": "Bialet Massé turismo naturaleza",
    "parque_relax": "naturaleza relax montaña Argentina",
    "familia_naturaleza": "familia vacaciones sierras cordoba",
    "cosquin": "Cosquin folklore sierras cordoba",
}

# Secuencia narrativa por objetivo: alterna b-roll y fotos
SECUENCIA_POR_OBJETIVO: dict[str, list[dict]] = {
    "cta_reserva": [
        {"tipo": "broll_youtube", "broll_tipo": "rio_agua", "duracion_seg": 4.5},
        {"tipo": "foto", "slot": 0, "duracion_seg": 3.8, "effect": "zoom_in"},
        {"tipo": "broll_youtube", "broll_tipo": "lago", "duracion_seg": 4.0},
        {"tipo": "foto", "slot": 1, "duracion_seg": 3.6, "effect": "drift_zoom"},
        {"tipo": "foto", "slot": 2, "duracion_seg": 3.4, "effect": "zoom_out"},
        {"tipo": "cierre", "duracion_seg": 4.0},
    ],
    "fidelizacion": [
        {"tipo": "broll_youtube", "broll_tipo": "parque_relax", "duracion_seg": 4.0},
        {"tipo": "foto", "slot": 0, "duracion_seg": 3.8, "effect": "drift_zoom"},
        {"tipo": "broll_youtube", "broll_tipo": "bialet", "duracion_seg": 3.8},
        {"tipo": "foto", "slot": 1, "duracion_seg": 3.6, "effect": "zoom_in"},
        {"tipo": "cierre", "duracion_seg": 4.0},
    ],
    "utilidad": [
        {"tipo": "broll_youtube", "broll_tipo": "rio_agua", "duracion_seg": 4.2},
        {"tipo": "broll_youtube", "broll_tipo": "bialet", "duracion_seg": 3.8},
        {"tipo": "foto", "slot": 0, "duracion_seg": 3.6, "effect": "pan_right"},
        {"tipo": "foto", "slot": 1, "duracion_seg": 3.4, "effect": "zoom_in"},
        {"tipo": "cierre", "duracion_seg": 3.8},
    ],
    "branding": [
        {"tipo": "broll_youtube", "broll_tipo": "sierras", "duracion_seg": 4.5},
        {"tipo": "foto", "slot": 0, "duracion_seg": 4.0, "effect": "zoom_in"},
        {"tipo": "broll_youtube", "broll_tipo": "lago", "duracion_seg": 4.0},
        {"tipo": "foto", "slot": 1, "duracion_seg": 3.6, "effect": "drift_zoom"},
        {"tipo": "cierre", "duracion_seg": 4.0},
    ],
}
