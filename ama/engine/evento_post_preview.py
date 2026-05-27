"""
Vista previa de publicación por evento — foto real + copy desde plantillas (sin inventar fechas).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ama.engine.content_strategist import generar_copy

_REPO = Path(__file__).resolve().parent.parent.parent
_FOTOS = _REPO / "archivos multimedia" / "fotos terra natura"
_ASSETS = _REPO / "ama" / "output" / "assets"

_IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Fotos fijas del complejo (siempre disponibles en disco del dueño)
_FALLBACK_CABANA = [
    "PARQUE/VISTA PANORAMICA DESDE EL COMPLEJO A TODO EL VALLE DE PUNILLA.jpg",
    "exteriores cabanas/VISTA PANORAMICA DEL COMPLEJO.jpg",
    "PISCINA/PARQUE Y PISCINA.jpg",
    "RIO Y BALNEARIOS/RIO COSQUIN EN BIALET MASSE.jpg",
    "RIO Y BALNEARIOS/TOMANDO UNOS MATES EN LOS LABIOS DEL INDIO EN BIALET MASSE.jpg",
]

_KEMPES_ASSETS = [
    "kempes_aereo.jpg",
    "kempes_post_partido.jpg",
    "belgrano_estadio_2025.jpg",
]


def _url_media(rel: str) -> str:
    """Ruta servida por /api/programa/media/…"""
    return "/api/programa/media/" + rel.replace("\\", "/")


def _url_asset(name: str) -> str:
    return f"/api/programa/assets/{name}"


def _existe_rel(rel: str) -> bool:
    p = _FOTOS / rel
    return p.is_file()


def _buscar_en_carpeta(carpeta: str, *keywords: str) -> str | None:
    base = _FOTOS / carpeta
    if not base.is_dir():
        return None
    kws = [k.lower() for k in keywords if k]
    candidatos: list[Path] = []
    for p in base.rglob("*"):
        if p.suffix.lower() not in _IMG_EXT:
            continue
        nombre = p.name.lower()
        if not kws or any(k in nombre for k in kws):
            candidatos.append(p)
    if not candidatos:
        return None
    candidatos.sort(key=lambda x: x.name)
    rel = candidatos[0].relative_to(_FOTOS).as_posix()
    return rel


def _match_festival(nombre: str, localidad: str) -> str | None:
    texto = f"{nombre} {localidad}".lower()
    reglas = [
        (("cosquin", "folklore", "folclore"), ("cosquin", "folklore", "folclore")),
        (("cosquin", "rock"), ("cosquin", "rock")),
        (("avicultura",), ("avicultura",)),
        (("carnaval",), ("carnaval",)),
        (("oktober", "cerveza", "oktoberfest"), ("oktober", "cerveza", "vgb")),
        (("colectividad",), ("colectividad",)),
        (("peperina",), ("peperina",)),
        (("alien", "alienigena"), ("alien", "alienigena")),
        (("estacion", "korolova", "electron"), ("estacion", "electron")),
    ]
    for triggers, fest_kw in reglas:
        if any(t in texto for t in triggers):
            rel = _buscar_en_carpeta("FESTIVALES", *fest_kw)
            if rel:
                return rel
            return None
    return None


def _foto_evento(ev: dict) -> tuple[str | None, str, bool]:
    """Returns (url, origen_label, es_foto_real_evento)"""
    nombre = (ev.get("nombre") or "").lower()
    loc = (ev.get("localidad") or "").lower()
    tipo = ev.get("tipo") or ""

    if any(x in nombre for x in ("kempes", "belgrano", "river", "copa argentina")):
        for a in _KEMPES_ASSETS:
            if (_ASSETS / a).is_file():
                return _url_asset(a), "assets/kempes", True

    rel = _match_festival(ev.get("nombre") or "", ev.get("localidad") or "")
    if rel and _existe_rel(rel):
        return _url_media(rel), "fotos/FESTIVALES", True

    if "carnaval" in nombre:
        rel = _buscar_en_carpeta("PARQUE") or _buscar_en_carpeta("RIO Y BALNEARIOS", "rio", "lago")
        if rel:
            return _url_media(rel), "complejo/carnaval", True

    if "carlos paz" in loc or "san roque" in loc or "dique" in loc:
        rel = _buscar_en_carpeta("RIO Y BALNEARIOS", "lago", "rio", "dique")
        if rel:
            return _url_media(rel), "fotos/lago", True

    if tipo in ("finde_largo", "feriado_nacional", "vacaciones_invierno", "promo_invierno"):
        for rel in _FALLBACK_CABANA:
            if _existe_rel(rel):
                return _url_media(rel), "complejo/puente", True

    if "bialet" in loc or tipo == "evento_local":
        rel = _buscar_en_carpeta("PARQUE") or _buscar_en_carpeta("PISCINA")
        if rel:
            return _url_media(rel), "complejo/bialet", True

    if ev.get("categoria") == "electronica" or "estacion" in nombre:
        rel = _buscar_en_carpeta("RIO Y BALNEARIOS", "lago") or _buscar_en_carpeta("PARQUE", "atardecer", "vista")
        if rel:
            return _url_media(rel), "fotos/entorno", True

    for rel in _FALLBACK_CABANA:
        if _existe_rel(rel):
            return _url_media(rel), "complejo/fallback", True

    return None, "sin_foto", False


def _angulo_marketing(ev: dict) -> str:
    if ev.get("angulo_comercial"):
        return str(ev["angulo_comercial"])
    if ev.get("copy_hook"):
        return str(ev["copy_hook"])
    if ev.get("mensaje_campana"):
        return str(ev["mensaje_campana"])
    if ev.get("oferta_sugerida"):
        return str(ev["oferta_sugerida"])
    if ev.get("descripcion"):
        return str(ev["descripcion"])[:280]
    return ""


def _tema_y_angulo_tpl(ev: dict) -> tuple[str, str]:
    nombre = (ev.get("nombre") or "").lower()
    tipo = ev.get("tipo") or ""
    if tipo in ("finde_largo", "feriado_nacional", "vacaciones_invierno", "promo_invierno"):
        return "feriado_puente", "parejas"
    if "familia" in nombre or "niño" in nombre or ev.get("categoria") == "familia":
        return "verano", "familia"
    if any(x in nombre for x in ("kempes", "feria", "colectividad", "oktober", "festival", "cosquin")):
        return "verano", "evento"
    if tipo in ("evento_confirmado", "evento_masivo", "evento_agenda", "evento_grilla"):
        return "verano", "evento"
    return "verano", "parejas"


def _titulo_post(ev: dict) -> str:
    nombre = (ev.get("nombre") or "Terra Natura").strip()
    loc = (ev.get("localidad") or "").strip()
    if loc and loc.lower() not in nombre.lower():
        return f"{nombre} · {loc}"
    return nombre


def _fecha_legible(ev: dict) -> str:
    fi = ev.get("fecha_inicio") or ev.get("fecha")
    ff = ev.get("fecha_fin")
    if not fi:
        return ""
    meses = (
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    )
    try:
        y, m, d = [int(x) for x in str(fi)[:10].split("-")]
        txt = f"{d} {meses[m - 1]} {y}"
        if ff and ff != fi:
            y2, m2, d2 = [int(x) for x in str(ff)[:10].split("-")]
            if (y, m) == (y2, m2):
                txt = f"{d} al {d2} de {meses[m - 1]} {y}"
            else:
                txt += f" – {d2} {meses[m2 - 1]} {y2}"
        return txt
    except (ValueError, IndexError):
        return str(fi)


def enriquecer_post_preview(ev: dict) -> dict:
    """Agrega post_preview y banner_url al ítem de agenda."""
    out = dict(ev)
    from ama.engine.evento_relevancia_bialet import enriquecer_angulo_comercial

    out = enriquecer_angulo_comercial(out)

    foto_url, foto_origen, foto_real = _foto_evento(out)
    angulo_txt = _angulo_marketing(out)
    tema, ang_tpl = _tema_y_angulo_tpl(out)

    cuerpo = angulo_txt
    if out.get("tipo") == "finde_largo" and out.get("cantidad_noches"):
        cuerpo += f"\n\nSugerimos {out['cantidad_noches']} noches en Bialet Massé."

    copy_pack = generar_copy(
        angulo=ang_tpl,
        canal="instagram",
        tema_extra=tema,
        cuerpo_extra=cuerpo or "Consultá disponibilidad en Terra Natura, Bialet Massé.",
    )

    titulo = _titulo_post(out)
    fecha_txt = _fecha_legible(out)

    # Copy final: título evento + ángulo real + CTA plantilla (sin datos inventados)
    lineas = [titulo]
    if fecha_txt:
        lineas.append(f"📅 {fecha_txt}")
    if angulo_txt:
        lineas.append("")
        lineas.append(angulo_txt)
    lineas.append("")
    lineas.append("Cabañas Alpinas Terra Natura · Los Talas 759, Bialet Massé")
    lineas.append(copy_pack.get("whatsapp_url", "").replace("https://", ""))

    copy_instagram = "\n".join(lineas).strip()
    hashtags = " ".join((copy_pack.get("hashtags") or [])[:6])

    try:
        from ama.engine.evento_publicaciones import plan_publicaciones

        out["plan_publicaciones"] = plan_publicaciones(out)
    except Exception:
        out["plan_publicaciones"] = None

    out["post_preview"] = {
        "titulo": titulo,
        "fecha_legible": fecha_txt,
        "banner_url": foto_url,
        "foto_post_url": foto_url,
        "foto_origen": foto_origen,
        "tiene_foto_real": foto_real,
        "copy_instagram": copy_instagram,
        "copy_con_hashtags": f"{copy_instagram}\n\n{hashtags}".strip(),
        "hashtags": copy_pack.get("hashtags") or [],
        "whatsapp_url": copy_pack.get("whatsapp_url"),
        "brief_visual": (
            f"Overlay: {titulo[:60]}. Foto: {foto_origen}. "
            "Logo Terra Natura abajo derecha."
        ),
        "estado_publicacion": "borrador_listo" if foto_real and angulo_txt else "falta_foto_o_copy",
    }
    if foto_url:
        out["banner_url"] = foto_url
    return out
