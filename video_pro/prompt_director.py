"""
Video Pro Creator — director creativo: pocos inputs → prompts cinematográficos (es-ES).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Variante = Literal["base", "cinematografica", "realista", "premium"]


@dataclass
class VideoProInputs:
    personajes: str
    ambientacion: str
    iluminacion: str
    estilo: str
    # Modo imagen
    prompt_imagen: str = ""
    modo: Literal["wizard", "imagen"] = "wizard"


def _limpiar(s: str) -> str:
    return (s or "").strip()


def _enriquecer_personaje(raw: str, variante: Variante) -> str:
    p = _limpiar(raw) or "protagonista con presencia marcada"
    extras = {
        "cinematografica": "expresión contenida, mirada dirigida a cámara o al horizonte, postura natural pero intencional",
        "realista": "aspecto humano auténtico, textura de piel natural, gestos creíbles sin artificio",
        "premium": "presencia editorial de lujo, elegancia en cada gesto, acabado de campaña high-end",
        "base": "carácter definido y memorable en encuadre cinematográfico",
    }
    return f"{p.capitalize()}. {extras[variante]}."


def _enriquecer_ambiente(raw: str, variante: Variante) -> str:
    a = _limpiar(raw) or "espacio contemporáneo con profundidad visual"
    capas = {
        "cinematografica": "composición en capas, fondo con bokeh suave, detalle arquitectónico o natural que refuerce la escena",
        "realista": "entorno creíble, materiales reconocibles, escala humana correcta, sin exceso de efectos",
        "premium": "locación aspiracional, líneas limpias, sensación de exclusividad y orden visual impecable",
        "base": "contexto espacial claro que sostenga la narrativa del plano",
    }
    return f"{a.capitalize()}. {capas[variante]}."


def _enriquecer_luz(raw: str, variante: Variante) -> str:
    l = _limpiar(raw).lower() or "luz cinematográfica suave"
    mapa = {
        "golden hour": "hora dorada, tonos cálidos en piel y sombras largas, atmósfera emocional",
        "atardecer": "atardecer con degradado cálido en el cielo, contraluz suave",
        "amanecer": "primeras luces del día, niebla ligera opcional, serenidad",
        "noche": "noche con fuentes puntuales, contrastes controlados, highlights en reflejos",
        "mañana": "luz matinal fresca, sombras definidas pero suaves",
        "tarde": "luz lateral de tarde, volumen en rostros y objetos",
    }
    for k, v in mapa.items():
        if k in l:
            l = v
            break
    refuerzo = {
        "cinematografica": "esquema de iluminación tipo película, relación key/fill cuidada, halación sutil permitida",
        "realista": "iluminación natural coherente con la hora y el espacio, sin sobreprocesado",
        "premium": "iluminación de estudio disimulada en exteriores, acabado de marca de lujo",
        "base": "exposición equilibrada, rango dinámico cinematográfico",
    }
    return f"{l.capitalize()}. {refuerzo[variante]}."


def _enriquecer_estilo(raw: str, variante: Variante) -> str:
    e = _limpiar(raw) or "cinematográfico premium"
    estilos = {
        "cinematografica": "estética de largometraje independiente, grano fino, color grading teal & orange moderado, 24 fps, sensación anamórfica",
        "realista": "hiperrealismo limpio, colores fieles, nitidez en detalle, sensación documental premium",
        "premium": "publicidad de lujo, fashion film, movimientos de cámara fluidos, pulido impecable, sin artificios baratos",
        "base": "calidad broadcast premium, composición cuidada, movimiento de cámara motivado",
    }
    if variante != "base":
        return estilos[variante]
    if any(x in e.lower() for x in ("lujo", "premium", "fashion", "comercial")):
        return estilos["premium"]
    if "realista" in e.lower():
        return estilos["realista"]
    return f"{e.capitalize()}. {estilos['cinematografica']}."


def _camara_y_movimiento(variante: Variante) -> str:
    m = {
        "cinematografica": "Travelling lento o dolly suave; plano medio o plano entero; profundidad de campo moderada; movimiento imperceptible para dar vida.",
        "realista": "Cámara al hombro estabilizada o trípode; encuadre natural; sin movimientos dramáticos innecesarios.",
        "premium": "Movimiento fluido tipo slider o gimbal; composición simétrica o regla de tercios refinada; transición elegante entre micro-acciones.",
        "base": "Un solo movimiento de cámara claro, sin cortes, duración 4–6 segundos.",
    }
    return m[variante]


def generar_paquete(inputs: VideoProInputs, variante: Variante = "base") -> dict:
    """Genera resumen, descripción visual y prompt final en español de España."""
    personaje = _enriquecer_personaje(inputs.personajes, variante)
    ambiente = _enriquecer_ambiente(inputs.ambientacion, variante)
    luz = _enriquecer_luz(inputs.iluminacion, variante)
    estilo_txt = _enriquecer_estilo(inputs.estilo, variante)
    camara = _camara_y_movimiento(variante)

    if inputs.modo == "imagen" and inputs.prompt_imagen:
        accion = _limpiar(inputs.prompt_imagen)
        resumen = (
            f"Vídeo corto generado a partir de imagen de referencia: {accion[:120]}… "
            f"Ambiente coherente con {inputs.ambientacion or 'la fotografía'}."
        )
    else:
        resumen = (
            f"Vídeo corto premium protagonizado por {inputs.personajes or 'el sujeto'}, "
            f"en {inputs.ambientacion or 'un entorno definido'}, con {inputs.iluminacion or 'luz trabajada'} "
            f"y estética {inputs.estilo or 'cinematográfica'}."
        )

    descripcion_visual = (
        f"En {ambiente} {luz} Aparece {personaje} "
        f"La dirección visual sigue un estilo {estilo_txt} {camara}"
    )

    prompt_final = (
        f"Genera un vídeo de 5 segundos en español (sin diálogos obligatorios, ambiente hispanohablante si hay texto). "
        f"Sujeto: {personaje} "
        f"Escena: {ambiente} "
        f"Iluminación: {luz} "
        f"Estilo: {estilo_txt} "
        f"Cámara: {camara} "
        f"Calidad 4K, sin deformaciones, sin texto flotante salvo que se indique. "
        f"Mantener continuidad y realismo premium."
    )
    if inputs.modo == "imagen":
        motion = _limpiar(inputs.prompt_imagen) or "movimiento sutil natural, parallax suave, vida en la escena"
        prompt_final = (
            f"Anima la imagen de referencia manteniendo identidad y composición. "
            f"Acción principal: {motion}. "
            f"Coherencia de luz: {luz}. "
            f"Estilo: {estilo_txt}. "
            f"{camara} "
            f"Sin morphing extraño ni artefactos. Duración 4–6 s."
        )

    return {
        "variante": variante,
        "resumen": resumen,
        "elementos": {
            "personajes": personaje,
            "ambientacion": ambiente,
            "iluminacion": luz,
            "estilo_visual": estilo_txt,
            "camara": camara,
        },
        "descripcion_visual": descripcion_visual,
        "prompt_final": prompt_final,
    }


def generar_completo(inputs: VideoProInputs) -> dict:
    base = generar_paquete(inputs, "base")
    return {
        "idioma": "es-ES",
        "modo": inputs.modo,
        "resumen": base["resumen"],
        "elementos_definidos": base["elementos"],
        "descripcion_visual": base["descripcion_visual"],
        "prompt_final": base["prompt_final"],
        "variantes": {
            "cinematografica": generar_paquete(inputs, "cinematografica"),
            "realista": generar_paquete(inputs, "realista"),
            "premium": generar_paquete(inputs, "premium"),
        },
    }
