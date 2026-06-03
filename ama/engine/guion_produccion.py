"""
Guion de producción por escena — calendario → B-roll YouTube + fotos justificadas → render.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any

from ama.engine.broll_queries import BROLL_POR_TIPO
from ama.engine.foto_catalogo import seleccionar_foto
from ama.engine.guion_produccion_store import fusionar_marcas_en_escenas
from ama.engine.script_generator import generar_guion, _lineas_hook, _lineas_emocion, _voz_off


def _texto_pantalla(lineas: list) -> str:
    if not lineas:
        return ""
    if isinstance(lineas[0], str):
        return " ".join(str(x) for x in lineas)
    parts = []
    for x in lineas:
        if isinstance(x, list):
            parts.append(" ".join(str(y) for y in x))
        else:
            parts.append(str(x))
    return " / ".join(parts)


def _detectar_arco(titulo: str, tipo_pieza: str, item: dict | None) -> str:
    t = (titulo or "").lower()
    if any(w in t for w in ("recorrido", "paseo", "48 h", "48h", "ruta", "camino")):
        return "recorrido_bialet"
    if any(w in t for w in ("rio", "arroyo", "agua", "lago", "dique", "san roque")):
        return "rio_lago"
    if any(w in t for w in ("pileta", "parque", "hamaca", "solarium")):
        return "parque_pileta"
    if any(w in t for w in ("cabaña", "cabana", "alpina", "suite", "refugio", "interior")):
        return "refugio_cabana"
    if item and (item.get("tipo") or "") == "finde_largo":
        return "finde_sierras"
    if tipo_pieza in ("promo_cta", "urgencia_lastminute"):
        return "cta_escapada"
    if tipo_pieza == "utilidad":
        return "tips_sierra"
    return "marca_emocion"


# Blueprints: título escena, prompt visual, broll_tipo, temas foto
_ARCOS: dict[str, list[dict]] = {
    "recorrido_bialet": [
        {
            "tipo": "hook_card",
            "titulo_escena": "Gancho — invitación al recorrido",
            "duracion_seg": 2.2,
        },
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Llegada por el lago",
            "broll_tipo": "lago",
            "descripcion_visual": (
                "Plano aéreo o travelling suave sobre el Dique San Roque / lago, "
                "luz de tarde, sensación de «ya llegaste» a las sierras. Sin logos ni texto en pantalla."
            ),
            "youtube_busqueda": "Dique San Roque drone cinematic 4k Bialet Massé",
            "duracion_seg": 5.0,
        },
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Sierras y valle",
            "broll_tipo": "sierras",
            "descripcion_visual": "Drone lento sobre sierras verdes y valle, cielo despejado, ritmo contemplativo.",
            "youtube_busqueda": "sierras Cordoba drone cinematic 4k naturaleza",
            "duracion_seg": 4.8,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Tu refugio — exterior cabaña",
            "temas_foto": ["alpina", "exterior", "bialet"],
            "keywords_foto": ["exterior", "fachada", "cabana", "terra"],
            "effect": "drift",
            "duracion_seg": 4.2,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Detalle que enamora — parque o pileta",
            "temas_foto": ["parque", "pileta"],
            "keywords_foto": ["parque", "pileta", "hamaca"],
            "effect": "slow_zoom_in",
            "duracion_seg": 4.0,
        },
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Atardecer en el entorno",
            "broll_tipo": "bialet",
            "descripcion_visual": "Atardecer dorado sobre montañas o agua; cierre emocional del recorrido.",
            "youtube_busqueda": "Bialet Massé atardecer sierras drone cinematic",
            "duracion_seg": 4.5,
        },
        {"tipo": "cierre", "titulo_escena": "Cierre + WhatsApp", "duracion_seg": 3.2},
    ],
    "rio_lago": [
        {"tipo": "hook_card", "titulo_escena": "Gancho — agua y sierras", "duracion_seg": 2.2},
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Agua y montaña",
            "broll_tipo": "rio_agua",
            "descripcion_visual": "Arroyo o río con sierras de fondo, movimiento de agua, sin gente en primer plano.",
            "youtube_busqueda": "rio sierras Cordoba drone cinematic 4k",
            "duracion_seg": 5.2,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Cerca del agua — Terra Natura",
            "temas_foto": ["rio", "lago"],
            "keywords_foto": ["rio", "lago", "agua"],
            "effect": "drift",
            "duracion_seg": 4.0,
        },
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Lago San Roque",
            "broll_tipo": "lago",
            "descripcion_visual": "Vista amplia del lago/dique, horizonte limpio, tono aspiracional.",
            "youtube_busqueda": "lago San Roque Cordoba drone atardecer 4k",
            "duracion_seg": 4.8,
        },
        {"tipo": "cierre", "titulo_escena": "Cierre", "duracion_seg": 3.2},
    ],
    "marca_emocion": [
        {"tipo": "hook_card", "titulo_escena": "Gancho emocional", "duracion_seg": 2.2},
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Paisaje serrano",
            "broll_tipo": "sierras",
            "descripcion_visual": "Montañas y cielo; calma; sin urbanización dominante.",
            "youtube_busqueda": "sierras Cordoba naturaleza cinematic broll 4k",
            "duracion_seg": 5.0,
        },
        {
            "tipo": "foto",
            "titulo_escena": "El predio",
            "temas_foto": ["parque", "bialet"],
            "keywords_foto": ["parque", "terra", "natura"],
            "effect": "hold",
            "duracion_seg": 4.2,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Refugio alpino",
            "temas_foto": ["alpina", "interior"],
            "keywords_foto": ["living", "interior", "balcon"],
            "effect": "drift",
            "duracion_seg": 4.0,
        },
        {"tipo": "cierre", "titulo_escena": "Cierre Terra Natura", "duracion_seg": 3.2},
    ],
    "refugio_cabana": [
        {"tipo": "hook_card", "titulo_escena": "Gancho — tu cabaña", "duracion_seg": 2.2},
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Entorno Bialet",
            "broll_tipo": "bialet",
            "descripcion_visual": "Drone sobre Bialet Massé o sierras cercanas, luz natural.",
            "youtube_busqueda": "Bialet Massé sierras drone cinematic",
            "duracion_seg": 4.8,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Fachada / entrada",
            "temas_foto": ["alpina", "suite"],
            "keywords_foto": ["exterior", "entrada"],
            "effect": "slow_zoom_in",
            "duracion_seg": 4.5,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Interior acogedor",
            "temas_foto": ["interior", "matrimonial"],
            "keywords_foto": ["dormitorio", "living", "matrimonial"],
            "effect": "drift",
            "duracion_seg": 4.0,
        },
        {"tipo": "cierre", "titulo_escena": "Reservá", "duracion_seg": 3.2},
    ],
    "parque_pileta": [
        {"tipo": "hook_card", "titulo_escena": "Gancho — relax", "duracion_seg": 2.2},
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Naturaleza y calma",
            "broll_tipo": "parque_relax",
            "descripcion_visual": "Bosque, montaña o jardín con luz suave; sensación de descanso.",
            "youtube_busqueda": "naturaleza montaña Argentina cinematic broll 4k",
            "duracion_seg": 4.8,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Pileta y parque",
            "temas_foto": ["pileta", "parque"],
            "keywords_foto": ["pileta", "parque", "hamaca"],
            "effect": "drift",
            "duracion_seg": 4.5,
        },
        {"tipo": "cierre", "titulo_escena": "Cierre", "duracion_seg": 3.2},
    ],
    "cta_escapada": [
        {"tipo": "hook_card", "titulo_escena": "Gancho — escapada", "duracion_seg": 2.0},
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Sierras + lago",
            "broll_tipo": "lago",
            "descripcion_visual": "Combinación agua y montaña; invita a reservar finde.",
            "youtube_busqueda": "Cordoba sierras lago drone cinematic 4k",
            "duracion_seg": 5.0,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Donde dormís",
            "temas_foto": ["alpina"],
            "keywords_foto": ["balcon", "vista", "cabaña"],
            "effect": "slow_zoom_in",
            "duracion_seg": 4.0,
        },
        {"tipo": "cierre", "titulo_escena": "WhatsApp", "duracion_seg": 3.5},
    ],
    "tips_sierra": [
        {"tipo": "hook_card", "titulo_escena": "Tip del día", "duracion_seg": 2.0},
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Contexto sierra",
            "broll_tipo": "bialet",
            "descripcion_visual": "Plano general de sierras o pueblo serrano, útil y claro.",
            "youtube_busqueda": "Bialet Massé sierras Cordoba drone",
            "duracion_seg": 4.5,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Base Terra Natura",
            "temas_foto": ["parque"],
            "keywords_foto": ["terra", "parque"],
            "effect": "pan_right",
            "duracion_seg": 3.8,
        },
        {"tipo": "cierre", "titulo_escena": "Guardá el tip", "duracion_seg": 3.0},
    ],
    "finde_sierras": [
        {"tipo": "hook_card", "titulo_escena": "Finde largo", "duracion_seg": 2.2},
        {
            "tipo": "broll_youtube",
            "titulo_escena": "Valle y sierras",
            "broll_tipo": "sierras",
            "descripcion_visual": "Valle amplio, drone, energía de escapada de finde.",
            "youtube_busqueda": "sierras Cordoba finde drone cinematic",
            "duracion_seg": 5.0,
        },
        {
            "tipo": "foto",
            "titulo_escena": "Tu base en Bialet",
            "temas_foto": ["bialet", "parque"],
            "keywords_foto": ["terra", "natura"],
            "effect": "drift",
            "duracion_seg": 4.0,
        },
        {"tipo": "cierre", "titulo_escena": "Reservá el finde", "duracion_seg": 3.5},
    ],
}


def resolver_pieza_calendario(
    hito_id: str,
    pieza_id: str,
    *,
    db: Any | None = None,
) -> dict | None:
    """Plan de campaña o pieza editorial del calendario."""
    if hito_id == "editorial-evergreen" and pieza_id.startswith("editorial|"):
        from ama.engine.piezas_editoriales import listar_piezas_editoriales
        from ama.engine.plan_marketing_unificado import desarrollar_pieza, _tipo_a_objetivo

        fecha_s = pieza_id.split("|", 1)[-1]
        try:
            d = date.fromisoformat(fecha_s)
        except ValueError:
            return None
        for ep in listar_piezas_editoriales(d, d):
            if ep.get("pieza_id") != pieza_id:
                continue
            tipo = ep.get("tipo_pieza") or "emocional_tema"
            pieza = {
                "id": pieza_id,
                "fecha_publicacion": fecha_s,
                "fecha_legible": ep.get("fecha_legible"),
                "titulo_publicacion": ep.get("titulo"),
                "tipo_pieza": tipo,
                "tipo_pieza_label": ep.get("tipo_pieza_label"),
                "ventana_label": ep.get("ventana_label"),
                "canal": ep.get("canal", "instagram"),
                "formato": ep.get("formato", "reel"),
            }
            item = {
                "nombre": ep.get("hito_nombre", "Calendario editorial"),
                "tipo": "editorial",
                "fecha_inicio": fecha_s,
            }
            return desarrollar_pieza(item, pieza, db=db)

    from ama.engine.plan_marketing_unificado import obtener_pieza

    return obtener_pieza(hito_id, pieza_id, db=db)


def _objetivo_pieza(pieza: dict) -> str:
    from ama.engine.plan_marketing_unificado import _tipo_a_objetivo

    return pieza.get("objetivo_editorial") or _tipo_a_objetivo(pieza.get("tipo_pieza") or "reflexivo_marca")


def generar_escenas_produccion(
    *,
    pieza: dict,
    item: dict | None,
    hook: str,
    objetivo: str,
    angulo: str,
    evento: dict | None,
) -> list[dict]:
    titulo = pieza.get("titulo_publicacion") or ""
    arco = _detectar_arco(titulo, pieza.get("tipo_pieza") or "", item)
    blueprint = _ARCOS.get(arco) or _ARCOS["marca_emocion"]
    lineas_pool = _lineas_emocion(objetivo, angulo, evento)
    fotos_usadas: set[str] = set()
    escenas: list[dict] = []
    num = 0

    for step in blueprint:
        num += 1
        tipo = step["tipo"]
        dur = float(step.get("duracion_seg", 3.5))
        lineas = (
            _lineas_hook(hook)
            if tipo == "hook_card"
            else (["Terra Natura", "Bialet Massé · Córdoba", "Reservá por WhatsApp"] if tipo == "cierre" else lineas_pool[num % len(lineas_pool)])
        )
        if tipo == "cierre":
            lineas = step.get("lineas") or ["Terra Natura", "Bialet Massé · Córdoba", "Reservá por WhatsApp"]

        base: dict[str, Any] = {
            "numero": num,
            "tipo": tipo,
            "titulo_escena": step.get("titulo_escena", tipo),
            "duracion_seg": dur,
            "lineas": lineas,
            "texto_pantalla": _texto_pantalla(lineas),
            "estado": "listo",
        }

        if tipo in ("broll_youtube", "clip_youtube"):
            broll_tipo = step.get("broll_tipo", "bialet")
            base.update(
                {
                    "broll_tipo": broll_tipo,
                    "broll_query": BROLL_POR_TIPO.get(broll_tipo, BROLL_POR_TIPO["bialet"]),
                    "descripcion_visual": step.get("descripcion_visual", ""),
                    "youtube_busqueda": step.get("youtube_busqueda", BROLL_POR_TIPO.get(broll_tipo, "")),
                    "youtube_id": None,
                    "youtube_url": None,
                    "youtube_inicio_seg": None,
                    "youtube_fin_seg": None,
                    "instruccion_usuario": (
                        "1) Copiá «youtube_busqueda» y buscá en YouTube (HD). "
                        "2) Elegí el clip y anotá minuto:segundo de INICIO y FIN. "
                        "3) Pegá el link o ID abajo."
                    ),
                    "estado": "pendiente_youtube",
                }
            )
        elif tipo == "foto":
            pick = seleccionar_foto(
                temas=step.get("temas_foto"),
                keywords=step.get("keywords_foto"),
                excluir=fotos_usadas,
            )
            ruta = pick.get("ruta") or ""
            if ruta:
                fotos_usadas.add(ruta)
            base.update(
                {
                    "effect": step.get("effect", "drift"),
                    "fuente": ruta,
                    "foto_ruta": ruta,
                    "foto_nombre": pick.get("nombre_archivo"),
                    "foto_justificacion": pick.get("justificacion"),
                    "foto_calidad": pick.get("calidad"),
                    "carpetas_sugeridas": pick.get("carpetas_sugeridas"),
                    "instruccion_usuario": "Foto elegida automáticamente. Podés cambiar la ruta si preferís otra.",
                    "estado": "listo" if ruta else "pendiente_foto",
                }
            )
        elif tipo == "hook_card":
            base["instruccion_usuario"] = "Texto de gancho; no requiere YouTube."
        elif tipo == "cierre":
            base["cta"] = "wa.me/5493541571190"
            base["instruccion_usuario"] = "Tarjeta final con marca y WhatsApp."

        escenas.append(base)
    return escenas


def generar_guion_produccion(
    pieza: dict,
    *,
    item: dict | None = None,
    db: Any | None = None,
    evento: dict | None = None,
) -> dict[str, Any]:
    """Guion enriquecido + guion_json listo para render tras marcar YouTube."""
    from ama.engine.content_strategist import generar_copy
    from ama.engine.media_picker import armar_assets

    objetivo = _objetivo_pieza(pieza)
    angulo = pieza.get("angulo") or "parejas"
    titulo = pieza.get("titulo_publicacion") or ""
    canal = pieza.get("canal") or "instagram"
    formato = pieza.get("formato") or "reel"

    if not pieza.get("copy_instagram"):
        copy_pack = generar_copy(
            angulo=angulo,
            canal=canal,
            tema_extra=pieza.get("ventana_label", ""),
        )
        pieza = {**pieza, "copy_instagram": copy_pack.get("copy", ""), "hashtags": copy_pack.get("hashtags", [])}

    evento_ctx = evento or (
        {
            "nombre": (item or {}).get("nombre"),
            "tipo": (item or {}).get("tipo"),
            "copy_hook": (item or {}).get("copy_hook"),
        }
        if item
        else None
    )

    assets = armar_assets(carpeta_media=None, db=db, tema_youtube=titulo[:40] or "Bialet", incluir_video=True)
    guion_base = generar_guion(
        objetivo=objetivo,
        canal=canal,
        formato=formato,
        angulo=angulo,
        titulo=titulo,
        evento=evento_ctx if (item or {}).get("tipo") == "finde_largo" else evento_ctx,
        assets=assets,
        estilo_reel="cinematico_profesional",
    )
    hook = guion_base.get("hook") or titulo
    escenas = generar_escenas_produccion(
        pieza=pieza,
        item=item,
        hook=hook,
        objetivo=objetivo,
        angulo=angulo,
        evento=evento_ctx,
    )
    pieza_id = pieza.get("id") or pieza.get("pieza_id") or ""
    escenas = fusionar_marcas_en_escenas(escenas, pieza_id)

    concepto = (
        f"Reel «{titulo}» — arco narrativo para {pieza.get('ventana_label') or 'calendario'}. "
        f"Alterná B-roll HD (vos marcás inicio/fin en YouTube) con fotos propias del complejo."
    )
    prompt_video_pro = _armar_prompt_video_pro(concepto, escenas, hook, guion_base.get("voz_off") or "")

    guion_json = _escenas_a_guion_json(escenas, guion_base, pieza)
    faltan = sum(1 for e in escenas if e.get("estado") == "pendiente_youtube")

    return {
        "concepto": concepto,
        "arco": _detectar_arco(titulo, pieza.get("tipo_pieza") or "", item),
        "hook": hook,
        "voz_off": guion_base.get("voz_off"),
        "duracion_total_seg": round(sum(float(e.get("duracion_seg", 3)) for e in escenas), 1),
        "escenas": escenas,
        "prompt_video_pro": prompt_video_pro,
        "guion_json": guion_json,
        "listo_para_render": faltan == 0,
        "escenas_pendientes_youtube": faltan,
        "checklist": [
            "Completá inicio/fin de cada escena YouTube en el calendario",
            "Revisá fotos sugeridas (cambiar ruta si hace falta)",
            "Tocá «Generar video» cuando todo esté en verde",
        ],
    }


def _armar_prompt_video_pro(concepto: str, escenas: list[dict], hook: str, voz: str) -> str:
    lines = [
        concepto,
        "",
        f"GANCHO: {hook}",
        f"VOZ OFF: {voz}",
        "",
        "ESCENAS (producción):",
    ]
    for e in escenas:
        n = e.get("numero")
        tit = e.get("titulo_escena", "")
        if e.get("tipo") in ("broll_youtube", "clip_youtube"):
            lines.append(f"\n{n}. [YouTube] {tit}")
            lines.append(f"   Visual: {e.get('descripcion_visual', '')}")
            lines.append(f"   Buscar en YouTube: {e.get('youtube_busqueda', '')}")
            if e.get("youtube_id"):
                lines.append(f"   ID: {e['youtube_id']} · inicio {e.get('youtube_inicio_seg')}s")
        elif e.get("tipo") == "foto":
            lines.append(f"\n{n}. [Foto] {tit}")
            lines.append(f"   Archivo: {e.get('foto_ruta') or e.get('fuente')}")
            lines.append(f"   Por qué: {e.get('foto_justificacion', '')}")
        else:
            lines.append(f"\n{n}. [{e.get('tipo')}] {tit} — {e.get('duracion_seg')}s")
    lines.append("\nMontaje: cinematográfico, fundidos suaves, música cálida, subtítulos.")
    return "\n".join(lines)


def _escenas_a_guion_json(escenas: list[dict], guion_base: dict, pieza: dict) -> dict:
    """Formato para editorial_reel_builder.build_from_guion."""
    out_escenas: list[dict] = []
    for e in escenas:
        tipo = e.get("tipo")
        row: dict[str, Any] = {
            "tipo": tipo,
            "duracion_seg": e.get("duracion_seg"),
            "lineas": e.get("lineas"),
            "texto_pantalla": e.get("texto_pantalla"),
        }
        if tipo in ("broll_youtube", "clip_youtube"):
            row["broll_tipo"] = e.get("broll_tipo")
            row["broll_query"] = e.get("broll_query") or e.get("youtube_busqueda")
            row["youtube_id"] = e.get("youtube_id")
            row["fuente"] = e.get("youtube_url") or e.get("youtube_id")
            if e.get("youtube_inicio_seg") is not None:
                row["youtube_inicio_seg"] = float(e["youtube_inicio_seg"])
            if e.get("youtube_fin_seg") is not None and e.get("youtube_inicio_seg") is not None:
                fin = float(e["youtube_fin_seg"])
                ini = float(e["youtube_inicio_seg"])
                if fin > ini:
                    row["duracion_seg"] = round(fin - ini, 2)
        elif tipo == "foto":
            row["fuente"] = e.get("foto_ruta") or e.get("fuente")
            row["effect"] = e.get("effect", "drift")
        elif tipo == "cierre":
            row["cta"] = e.get("cta", "wa.me/5493541571190")
        out_escenas.append(row)

    return {
        **{k: guion_base[k] for k in ("objetivo", "musica", "subtitulos") if k in guion_base},
        "objetivo": guion_base.get("objetivo"),
        "canal": pieza.get("canal", "instagram"),
        "formato": pieza.get("formato", "reel"),
        "hook": guion_base.get("hook"),
        "voz_off": guion_base.get("voz_off"),
        "escenas": out_escenas,
        "modo_profesional": True,
        "xfade_seg": 0.72,
        "estilo_reel": "cinematico_profesional",
    }


def adjuntar_guion_produccion(pieza_desarrollada: dict, *, item: dict | None, db: Any | None) -> dict:
    fmt = (pieza_desarrollada.get("formato") or "").lower()
    if fmt not in ("reel", "status"):
        return pieza_desarrollada
    gp = generar_guion_produccion(pieza_desarrollada, item=item, db=db)
    pieza_desarrollada["guion_produccion"] = gp
    pieza_desarrollada["prompt_video_pro"] = gp.get("prompt_video_pro")
    if gp.get("guion_json"):
        pieza_desarrollada["guion_json"] = gp["guion_json"]
    return pieza_desarrollada


def render_video_produccion(
    hito_id: str,
    pieza_id: str,
    *,
    db: Any | None = None,
) -> dict[str, Any]:
    pieza = resolver_pieza_calendario(hito_id, pieza_id, db=db)
    if not pieza:
        return {"ok": False, "error": "Pieza no encontrada"}

    item = {"nombre": pieza.get("hito_nombre"), "tipo": pieza.get("hito_tipo")}
    gp = generar_guion_produccion(pieza, item=item, db=db)
    if not gp.get("listo_para_render"):
        pend = gp.get("escenas_pendientes_youtube", 0)
        return {
            "ok": False,
            "error": f"Faltan {pend} escena(s) de YouTube: pegá ID y tiempo inicio/fin.",
            "guion_produccion": gp,
        }

    from ama.engine.media_picker import armar_assets
    from ama.video.editorial_reel_builder import build_from_guion

    assets = armar_assets(db=db, tema_youtube=pieza.get("titulo_publicacion", "Bialet")[:40])
    for e in gp.get("escenas") or []:
        if e.get("tipo") == "foto" and e.get("foto_ruta"):
            r = e["foto_ruta"]
            if r not in assets.get("fotos", []):
                assets.setdefault("fotos", []).append(r)

    slug = re.sub(r"[^\w]+", "_", pieza_id)[:40]
    result = build_from_guion(gp["guion_json"], assets=assets, pub_id=slug, db=db)
    result["guion_produccion"] = gp
    result["pieza_id"] = pieza_id
    return result
