"""
¿Este evento puede traer huéspedes a alojarse en Bialet Massé?
No: Rio Cuarto, interior lejano, etc.
Sí: Punilla, puentes, Kempes/Córdoba cercana (excursión + descanso en sierra).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent / "data"
_CRITERIOS = _DATA / "criterios_eventos_cabanas.json"

_TIPOS_ESCAPADA = frozenset(
    {
        "finde_largo",
        "feriado_nacional",
        "vacaciones_invierno",
        "promo_invierno",
        "dia_especial",
    }
)


def _criterios() -> dict:
    if not _CRITERIOS.is_file():
        return {}
    with _CRITERIOS.open(encoding="utf-8") as f:
        return json.load(f)


def _texto(ev: dict) -> str:
    parts = [
        ev.get("nombre") or "",
        ev.get("localidad") or "",
        ev.get("descripcion") or "",
        ev.get("categoria") or "",
    ]
    return " ".join(parts).lower()


def _km_desde_localidad(localidad: str | None, c: dict) -> float | None:
    if not localidad:
        return None
    loc = localidad.strip()
    nucleo = c.get("localidades_nucleo_km") or {}
    for nombre, km in nucleo.items():
        if nombre.lower() in loc.lower() or loc.lower() in nombre.lower():
            return float(km)
    return None


def evaluar_demanda_cabana(ev: dict) -> tuple[bool, str, str | None]:
    """
    Returns: (incluir, motivo_interno, angulo_comercial_sugerido)
    """
    c = _criterios()
    tipo = ev.get("tipo") or ""

    if tipo in _TIPOS_ESCAPADA or tipo in set(c.get("incluir_siempre") or []):
        angulo = "Escapada a las sierras — pileta, parque y dueños en el predio (Bialet Massé)."
        return True, "escapada_oficial", angulo

    texto = _texto(ev)
    for bloq in c.get("excluir_si_contiene") or []:
        if bloq in texto:
            return False, f"excluido:{bloq}", None

    km_ev = ev.get("distancia_km_bialet")
    if km_ev is None:
        km_ev = _km_desde_localidad(ev.get("localidad"), c)

    excursion_kw = c.get("excursion_keywords") or []
    es_excursion = any(k in texto for k in excursion_kw)
    km_max_exc = float(c.get("excursion_desde_bialet_km_max") or 55)
    km_max_sierra = float(c.get("sierra_excursion_km_max") or 75)
    angulo_base = (c.get("meta") or {}).get("angulo_excursion") or (
        "Alojate en Bialet (pileta, parque, tranquilo) y andá al evento — "
        "las sierras, Dique San Roque o excursión de día."
    )

    if es_excursion and (km_ev is None or km_ev <= km_max_exc):
        angulo = ev.get("angulo_comercial") or (
            "Viví el evento en Córdoba/Kempes y descansá en Bialet — "
            "~40 min por Autovía Serranías Puntanas, sin perder la sierra."
        )
        return True, "excursion_cordoba_cercana", angulo

    if km_ev is not None and km_ev <= km_max_sierra:
        nucleo = c.get("localidades_nucleo_km") or {}
        loc_ev = (ev.get("localidad") or "").lower()
        for nombre, km_loc in nucleo.items():
            if km_loc > km_max_exc and (
                nombre.lower() in loc_ev or loc_ev in nombre.lower()
            ):
                angulo = ev.get("angulo_comercial") or angulo_base
                return True, "excursion_sierra_lejana", angulo

    km_max = float(c.get("km_max_evento_generico") or 40)
    if km_ev is not None and km_ev <= km_max:
        angulo = ev.get("angulo_comercial") or (
            f"Evento en {ev.get('localidad') or 'la zona'} — alojate en Bialet (las sierras) y andá relajado."
        )
        return True, "punilla_cercano", angulo

    if km_ev is not None and km_ev > km_max_exc:
        return False, f"muy_lejos_{km_ev}km", None

    # Sin km: solo si menciona punilla / bialet / cosquin / carlos paz
    punilla_pat = re.compile(
        r"bialet|punilla|cosqu[ií]n|carlos paz|tanti|santa mar[ií]a de punilla|valle de punilla|"
        r"la falda|la cumbre|capilla del monte|villa general belgrano|alta gracia|"
        r"san roque|dique san roque|costa azul|la estaci[oó]n|comuna san roque|"
        r"oktoberfest|peperina|colectividades|alien[ií]gena|electron",
        re.I,
    )
    if punilla_pat.search(texto):
        return True, "texto_punilla", ev.get("angulo_comercial")

    return False, "sin_potencial_alojamiento_bialet", None


def enriquecer_angulo_comercial(ev: dict) -> dict:
    ok, motivo, angulo = evaluar_demanda_cabana(ev)
    out = dict(ev)
    out["potencial_cabaña"] = ok
    out["motivo_filtro"] = motivo
    if angulo and ok:
        out["angulo_comercial"] = angulo
    return out


def filtrar_demanda_cabana(items: list[dict]) -> list[dict]:
    out = []
    for it in items:
        ok, _, angulo = evaluar_demanda_cabana(it)
        if not ok:
            continue
        row = dict(it)
        row["potencial_cabaña"] = True
        if angulo:
            row["angulo_comercial"] = angulo
        out.append(row)
    return out
