"""
Plan de marketing unificado — zona + estrategia + desarrollo completo por pieza.
"""
from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from typing import Any

from ama.engine.estratega_dia import planificar_dia

_TIPO_PIEZA = {
    "promo_cta": "Oferta con reserva",
    "emocional_tema": "Emoción del momento",
    "reflexivo_marca": "Marca y descanso",
    "recordatorio_suave": "Recordatorio suave",
    "utilidad": "Tips para viajeros",
    "urgencia_lastminute": "Último momento",
}

_VENTANAS = [
    (60, "t60", "Planificar campaña"),
    (30, "t30", "Sembrar emoción"),
    (15, "t15", "Conectar con el tema"),
    (7, "t7", "Oferta o consultá fechas"),
    (0, "dia_d", "Día del evento"),
    (-2, "t_post", "Cierre / agradecimiento"),
]

_MESES = (
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)


def _fecha_hito(item: dict) -> date | None:
    raw = item.get("fecha_inicio") or item.get("fecha")
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def _intensidad(item: dict) -> str:
    t = (item.get("tipo") or "").lower()
    if t in ("finde_largo", "vacaciones_verano", "vacaciones_invierno"):
        return "alta"
    if t in ("dia_especial", "feriado_nacional"):
        return "media"
    return "baja"


def _tipo_a_objetivo(tipo_pieza: str) -> str:
    return {
        "promo_cta": "cta_reserva",
        "urgencia_lastminute": "cta_reserva",
        "emocional_tema": "fidelizacion",
        "recordatorio_suave": "fidelizacion",
        "utilidad": "utilidad",
        "reflexivo_marca": "branding",
    }.get(tipo_pieza, "branding")


def _angulo_hito(item: dict, tipo_pieza: str) -> str:
    t = (item.get("tipo") or "").lower()
    if t == "finde_largo":
        return "finde_largo"
    if t == "dia_especial":
        return "parejas"
    if "vacaciones" in t:
        return "familia"
    return "parejas" if tipo_pieza == "emocional_tema" else "parejas"


def _cuerpo_campana(item: dict, tipo_pieza: str, ventana_label: str, dias_antes: int) -> str:
    nombre = item.get("nombre") or "la fecha"
    hook = item.get("copy_hook") or ""
    if tipo_pieza == "promo_cta":
        return (
            f"Finde largo / {nombre}: quedan fechas en nuestras cabañas en Bialet Massé, "
            f"a 600 m del lago San Roque. Seña 50 % por WhatsApp. {hook}".strip()
        )
    if tipo_pieza == "emocional_tema":
        if dias_antes >= 30:
            return (
                f"Se acerca {nombre}. Pensá en regalar descanso en las sierras — "
                f"no hace falta un regalo material: una noche con vista y parque. {hook}"
            ).strip()
        return (
            f"¿Te imaginás un finde en Bialet? Cabaña, parque y lago a 600 m — "
            f"sin apuro de ciudad, con ganas de bajar un cambio. {hook}"
        ).strip()
    if tipo_pieza == "recordatorio_suave":
        return (
            f"¿Ya pensaste en {nombre}? Las sierras de Córdoba son el plan B perfecto. "
            f"Sin apuro — consultanos cuando quieras. {hook}"
        ).strip()
    if tipo_pieza == "utilidad":
        return (
            f"Hoy es {nombre}. Tips: paseo al lago, asado en la pérgola, silencio de sierra. "
            f"Si estás en Bialet, disfrutá el día."
        )
    if tipo_pieza == "urgencia_lastminute":
        return f"Últimos lugares para {nombre} — escribinos ya por WhatsApp."
    return (
        f"Terra Natura en Bialet Massé: naturaleza, pileta y cabañas alpinas. "
        f"Contexto: {nombre}. {hook}"
    ).strip()


def _piezas_para_hito(item: dict, ref: date, hito_id: str) -> list[dict]:
    fh = _fecha_hito(item)
    if not fh:
        return []
    t = (item.get("tipo") or "").lower()
    nombre = item.get("nombre") or "Hito"
    piezas: list[dict] = []

    def add(dias_antes: int, ventana_id: str, ventana_label: str) -> None:
        disparo = fh - timedelta(days=dias_antes)
        if dias_antes < 0:
            disparo = fh + timedelta(days=abs(dias_antes))
        if t == "finde_largo":
            if dias_antes >= 30:
                tipo = "recordatorio_suave"
            elif dias_antes >= 15:
                tipo = "emocional_tema"
            elif dias_antes >= 7:
                tipo = "promo_cta"
            elif dias_antes == 0:
                tipo = "utilidad"
            else:
                tipo = "reflexivo_marca"
        elif t == "dia_especial":
            if dias_antes >= 30:
                tipo = "emocional_tema"
            elif dias_antes >= 15:
                tipo = "emocional_tema"
            elif dias_antes >= 7:
                tipo = "recordatorio_suave"
            elif dias_antes == 0:
                tipo = "emocional_tema"
            else:
                tipo = "reflexivo_marca"
        else:
            tipo = "emocional_tema" if dias_antes >= 15 else "promo_cta"

        pieza_id = f"{hito_id}|{ventana_id}|{disparo.isoformat()}"
        piezas.append(
            {
                "id": pieza_id,
                "ventana": ventana_id,
                "ventana_label": ventana_label,
                "dias_antes": dias_antes,
                "fecha_publicacion": disparo.isoformat(),
                "fecha_legible": disparo.strftime("%d/%m/%Y"),
                "hora_sugerida": "10:00",
                "canal": "instagram",
                "formato": "reel",
                "tipo_pieza": tipo,
                "tipo_pieza_label": _TIPO_PIEZA.get(tipo, tipo),
                "hito_nombre": nombre,
                "estado": _estado_pieza(disparo, ref),
                "titulo_publicacion": _titulo_pieza(tipo, nombre, ventana_label),
            }
        )

    for dias, vid, vlabel in _VENTANAS:
        add(dias, vid, vlabel)

    return piezas


def _titulo_pieza(tipo: str, nombre: str, ventana: str) -> str:
    pref = {
        "promo_cta": f"Reservá tu lugar — {nombre}",
        "emocional_tema": f"Escapada para {nombre}",
        "recordatorio_suave": f"Se acerca {nombre}",
        "utilidad": f"Disfrutá {nombre} en las sierras",
        "reflexivo_marca": f"Terra Natura · {nombre}",
        "urgencia_lastminute": f"Último momento — {nombre}",
    }
    return pref.get(tipo, f"{ventana} — {nombre}")


def _estado_pieza(fecha_pieza: date, hoy: date) -> str:
    if fecha_pieza < hoy - timedelta(days=2):
        return "pasada"
    if fecha_pieza == hoy:
        return "hoy"
    if hoy < fecha_pieza <= hoy + timedelta(days=7):
        return "proxima"
    return "planificada"


def _plan_accion_hito(item: dict, piezas: list[dict]) -> dict:
    nombre = item.get("nombre") or "Campaña"
    t = (item.get("tipo") or "").lower()
    fi = item.get("fecha_inicio") or item.get("fecha")
    ff = item.get("fecha_fin") or fi

    fases = []
    if t == "finde_largo":
        fases = [
            {
                "nombre": "Fase 1 — Sembrar (T-60 a T-30)",
                "que_hacemos": "Recordatorios suaves y marca: sin precio agresivo.",
                "piezas": [p["fecha_legible"] for p in piezas if p["dias_antes"] >= 30],
            },
            {
                "nombre": "Fase 2 — Emoción (T-30 a T-15)",
                "que_hacemos": "Conectar con el finde largo: regalo experiencia, sierras, pareja/familia.",
                "piezas": [p["fecha_legible"] for p in piezas if 15 <= p["dias_antes"] < 30],
            },
            {
                "nombre": "Fase 3 — Conversión (T-15 a T-7)",
                "que_hacemos": "CTA WhatsApp con fechas libres y seña 50 %.",
                "piezas": [p["fecha_legible"] for p in piezas if 7 <= p["dias_antes"] < 15],
            },
            {
                "nombre": "Fase 4 — Día D y cierre",
                "que_hacemos": "Mensaje del día + agradecimiento / prueba social.",
                "piezas": [p["fecha_legible"] for p in piezas if p["dias_antes"] <= 0],
            },
        ]

    calendario_pub = [
        {
            "fecha": p["fecha_legible"],
            "titulo": p.get("titulo_publicacion"),
            "tipo": p.get("tipo_pieza_label"),
            "ventana": p.get("ventana_label"),
            "canal": "Instagram (reel)",
        }
        for p in sorted(piezas, key=lambda x: x["fecha_publicacion"])
        if p["estado"] != "pasada"
    ]

    return {
        "resumen": (
            f"Campaña «{nombre}» ({fi} al {ff}): publicamos en fechas clave "
            f"antes del hito para emocionar, informar y cerrar reservas."
        ),
        "fases": fases,
        "calendario_publicaciones": calendario_pub,
        "total_publicaciones": len(calendario_pub),
    }


def _estrategia_hito(item: dict) -> str:
    from datetime import date as _date

    from ama.engine.comercial_2026 import estrategia_para_fecha, finde_largo_en_fecha

    n = item.get("nombre") or "este período"
    fi = item.get("fecha_inicio")
    try:
        d = _date.fromisoformat(str(fi)[:10]) if fi else _date.today()
    except ValueError:
        d = _date.today()
    finde = finde_largo_en_fecha(d)
    if finde and finde.get("nombre"):
        return (
            f"{finde['nombre']}: {estrategia_para_fecha(d)} "
            f"Promo sugerida: {finde.get('promo', '')}. "
            "Calendario: docs/CALENDARIO_COMERCIAL_2026.md"
        )
    base = estrategia_para_fecha(d)
    t = (item.get("tipo") or "").lower()
    if t == "finde_largo":
        return f"Finde largo {n}: {base}"
    if t == "dia_especial":
        return f"{n}: regalar experiencia en las sierras; {base}"
    if "vacaciones" in t:
        return f"{n}: familias y parejas; {base} Promo invierno 5+1 en julio."
    return f"{n}: {base}"


def _cuerpo_editorial(tipo_pieza: str, titulo_pieza: str) -> str:
    """Copy pegable en IG — sin nombres de campaña ni tono 'rehabilitación'."""
    t = (titulo_pieza or "").strip()
    if tipo_pieza == "emocional_tema":
        if t:
            return (
                f"{t} Cabañas alpinas y suites en Bialet Massé: parque, pileta al sol "
                f"y lago San Roque a 600 m. Finde para bajar un cambio — "
                f"los dueños estamos en el predio."
            )
        return (
            "Un finde en las sierras: silencio, parque, pileta al sol y el lago cerca. "
            "Cinco cabañas en Bialet Massé — los dueños estamos en el predio si necesitás algo."
        )
    if tipo_pieza == "utilidad":
        return (
            "Tip desde Bialet: dos noches rinden más que una para cortar el ritmo de la semana. "
            "Río a la mañana, pileta a la tarde (horario de temporada), asado en la pérgola. "
            "Consultá fechas cuando quieras."
        )
    if tipo_pieza == "reflexivo_marca":
        return (
            "Así es acá: predio de ~2.000 m², pileta 6×3 m, hamacas y cabañas alpinas con vista. "
            "No es un hotel masivo — es escapada a las sierras con atención de quien vive en el lugar."
        )
    return (
        "Escapada a las sierras de Córdoba, en Bialet Massé. "
        "Alpinas para pareja o familia chica · Suites loft · reserva directa."
    )


def desarrollar_pieza(item: dict, pieza: dict, *, db: Any | None = None) -> dict:
    """Genera copy, guion y brief creativo completos para una pieza del plan."""
    from ama.engine.content_strategist import generar_copy
    from ama.engine.script_generator import generar_guion

    tipo = pieza.get("tipo_pieza") or "reflexivo_marca"
    objetivo = _tipo_a_objetivo(tipo)
    angulo = _angulo_hito(item, tipo)
    es_editorial = bool(pieza.get("es_editorial")) or (item.get("tipo") or "").lower() == "editorial"
    titulo_pub = (pieza.get("titulo") or pieza.get("titulo_publicacion") or "").strip()

    if es_editorial:
        cuerpo = _cuerpo_editorial(tipo, titulo_pub)
    else:
        cuerpo = _cuerpo_campana(
            item, tipo, pieza.get("ventana_label", ""), pieza.get("dias_antes", 0)
        )

    evento_ctx = {
        "nombre": item.get("nombre"),
        "tipo": item.get("tipo"),
        "copy_hook": item.get("copy_hook"),
        "fecha_inicio": item.get("fecha_inicio"),
    }

    copy_pack = generar_copy(
        angulo=angulo,
        canal="instagram",
        tema_extra="",
        cuerpo_extra=cuerpo,
        titulo=titulo_pub or None,
    )

    guion = generar_guion(
        objetivo=objetivo,
        canal="instagram",
        formato="reel",
        angulo=angulo,
        titulo=pieza.get("titulo_publicacion") or copy_pack.get("titulo", ""),
        evento=evento_ctx if item.get("tipo") == "finde_largo" else evento_ctx,
    )

    escenas_txt = []
    for i, esc in enumerate(guion.get("escenas") or [], 1):
        lineas = esc.get("lineas") or []
        if isinstance(lineas, list) and lineas and isinstance(lineas[0], list):
            txt = " / ".join(" ".join(x) if isinstance(x, list) else str(x) for x in lineas)
        elif isinstance(lineas, list):
            txt = " ".join(str(x) for x in lineas)
        else:
            txt = str(lineas)
        escenas_txt.append(
            {
                "numero": i,
                "tipo": esc.get("tipo"),
                "duracion_seg": esc.get("duracion_seg"),
                "texto_pantalla": txt or esc.get("texto_pantalla"),
                "notas": esc.get("broll_query") or esc.get("fuente") or "",
            }
        )

    promo_comercial = ""
    try:
        from datetime import date as _date

        from ama.engine.comercial_2026 import promo_recomendada, tarifa_orientativa_noche

        fp = pieza.get("fecha_publicacion")
        if fp:
            fd = _date.fromisoformat(str(fp)[:10])
            pr = promo_recomendada(fd)
            tarifa = tarifa_orientativa_noche(fd, "alpina")
            tarifa_txt = f"${tarifa:,}".replace(",", ".")
            promo_comercial = (
                f"\nCOMERCIAL 2026:\n"
                f"  Tarifa orientativa Alpina/noche: {tarifa_txt}\n"
                f"  Promo sugerida: {pr.get('promo') or pr.get('texto_publico') or pr.get('codigo')}\n"
            )
    except Exception:
        pass

    brief_prompt = (
        f"Campaña: {item.get('nombre')}\n"
        f"Ventana: {pieza.get('ventana_label')} ({pieza.get('fecha_legible')})\n"
        f"Tipo: {pieza.get('tipo_pieza_label')}\n"
        f"Objetivo editorial: {objetivo}\n"
        f"{promo_comercial}\n"
        f"COPY INSTAGRAM:\n{copy_pack.get('copy', '')}\n\n"
        f"GANCHO REEL: {guion.get('hook', '')}\n"
        f"VOZ EN OFF: {guion.get('voz_off', '')}\n\n"
        f"ESCENAS ({len(escenas_txt)}):\n"
        + "\n".join(
            f"  {e['numero']}. [{e['tipo']}] {e['duracion_seg']}s — {e['texto_pantalla']}"
            for e in escenas_txt
        )
    )

    resultado = {
        **pieza,
        "desarrollado": True,
        "objetivo_editorial": objetivo,
        "objetivo_editorial_label": {
            "cta_reserva": "Reserva / CTA",
            "fidelizacion": "Vínculo (sin CTA duro)",
            "utilidad": "Utilidad / tips",
            "branding": "Marca / experiencia",
        }.get(objetivo, objetivo),
        "titulo_publicacion": titulo_pub or copy_pack.get("titulo", ""),
        "angulo": angulo,
        "copy_instagram": copy_pack.get("copy", ""),
        "hashtags": copy_pack.get("hashtags", []),
        "whatsapp_url": copy_pack.get("whatsapp_url"),
        "brief_creativo": copy_pack.get("brief_canva"),
        "brief_prompt": brief_prompt,
        "guion": {
            "hook": guion.get("hook"),
            "voz_off": guion.get("voz_off"),
            "duracion_total_seg": guion.get("duracion_total_seg"),
            "musica": guion.get("musica"),
            "escenas": escenas_txt,
            "checklist": guion.get("checklist_pre_publicar"),
        },
        "guion_json": guion,
    }
    from ama.engine.guion_produccion import adjuntar_guion_produccion

    return adjuntar_guion_produccion(resultado, item=item, db=db)


def _filtrar_item_agenda(it: dict) -> tuple[bool, str]:
    tipo = it.get("tipo") or ""
    if tipo in ("referencia",):
        return False, "tipo_referencia"

    nombre_l = (it.get("nombre") or "").lower()
    categoria_l = (it.get("categoria") or "").lower()
    blob = f"{nombre_l} {categoria_l} {(it.get('localidad') or '').lower()}"

    if "teatro" in blob and tipo not in ("finde_largo", "dia_especial"):
        return False, "teatro_sin_pernocte"

    ferias_grandes = (
        "cosquín",
        "cosquin",
        "kempes",
        "oktoberfest",
        "peperina",
        "feria de córdoba",
        "colectividades",
    )
    if "feria" in blob and not any(g in blob for g in ferias_grandes):
        return False, "feria_chica"

    from ama.engine.distancia_bialet import distancia_desde_bialet
    from ama.engine.evento_relevancia_bialet import evaluar_demanda_cabana

    it_eval = dict(it)
    if tipo in ("evento_cordoba_turismo", "evento_grilla", "evento_agenda"):
        it_eval["distancia_km_bialet"] = None

    info = distancia_desde_bialet(it_eval, km_max=60.0)
    it = {**it, "distancia_km_bialet": info.get("km"), "filtro_distancia": info}

    if not info.get("dentro_radio"):
        return False, info.get("motivo") or "fuera_60km"

    _escapadas = frozenset(
        {
            "finde_largo",
            "feriado_nacional",
            "vacaciones_invierno",
            "vacaciones_verano",
            "promo_invierno",
            "promo_verano",
            "dia_especial",
        }
    )
    if tipo not in _escapadas:
        rel, motivo, _ = evaluar_demanda_cabana(it)
        if not rel:
            return False, motivo
    return True, "ok"


def _construir_hitos(
    items: list[dict],
    hoy: date,
    *,
    desarrollar_todas_piezas: bool = False,
    desarrollar_hasta: date | None = None,
    db: Any | None = None,
) -> list[dict]:
    desarrollar_hasta = desarrollar_hasta or (hoy + timedelta(days=120))
    hitos: list[dict] = []

    for it in sorted(items, key=lambda x: x.get("orden", "")):
        ok, motivo = _filtrar_item_agenda(it)
        if not ok:
            continue
        fh = _fecha_hito(it)
        if not fh:
            continue
        hito_id = f"{it.get('tipo','h')}-{fh.isoformat()}-{hash(it.get('nombre','')) % 100000}"
        dias_hasta = (fh - hoy).days
        piezas = _piezas_para_hito(it, hoy, hito_id)

        desarrollar = desarrollar_todas_piezas or any(
            date.fromisoformat(p["fecha_publicacion"]) <= desarrollar_hasta
            for p in piezas
        )

        piezas_out = []
        for p in piezas:
            if desarrollar or p["estado"] in ("hoy", "proxima") or dias_hasta <= 45:
                piezas_out.append(desarrollar_pieza(it, p, db=db))
            else:
                piezas_out.append({**p, "desarrollado": False})

        hitos.append(
            {
                "id": hito_id,
                "nombre": it.get("nombre"),
                "tipo": it.get("tipo"),
                "localidad": it.get("localidad"),
                "distancia_km": it.get("distancia_km_bialet"),
                "fecha_inicio": it.get("fecha_inicio") or it.get("fecha"),
                "fecha_fin": it.get("fecha_fin"),
                "dias_hasta": dias_hasta,
                "intensidad": _intensidad(it),
                "estrategia": _estrategia_hito(it),
                "plan_accion": _plan_accion_hito(it, piezas_out),
                "que_pasa_zona": it.get("nombre"),
                "piezas": piezas_out,
                "pieza_hoy": next((p for p in piezas_out if p.get("estado") == "hoy"), None),
                "pieza_proxima": next((p for p in piezas_out if p.get("estado") == "proxima"), None),
            }
        )
    return hitos


def _agrupar_por_mes(hitos: list[dict], anio: int) -> list[dict]:
    meses: dict[int, list] = {m: [] for m in range(1, 13)}
    for h in hitos:
        fh = _fecha_hito(h)
        if not fh or fh.year != anio:
            continue
        meses[fh.month].append(h)

    out = []
    for m in range(1, 13):
        lista = sorted(meses[m], key=lambda x: x.get("fecha_inicio") or "")
        out.append(
            {
                "anio": anio,
                "mes": m,
                "mes_label": _MESES[m - 1],
                "clave": f"{anio}-{m:02d}",
                "hitos": lista,
                "total_hitos": len(lista),
                "total_publicaciones": sum(
                    len(h.get("plan_accion", {}).get("calendario_publicaciones") or [])
                    for h in lista
                ),
            }
        )
    return out


def _elegir_campaña_activa(hitos: list[dict], hoy: date) -> dict | None:
    def _prio(h: dict) -> tuple:
        t = (h.get("tipo") or "").lower()
        tipo_ord = {
            "finde_largo": 0,
            "dia_especial": 1,
            "vacaciones_invierno": 2,
            "vacaciones_verano": 2,
            "feriado_nacional": 3,
        }.get(t, 8)
        intens = 0 if h.get("intensidad") == "alta" else 1
        dias = h.get("dias_hasta") if h.get("dias_hasta") is not None else 9999
        return (tipo_ord, intens, dias)

    candidatos = sorted(hitos, key=_prio)
    for h in candidatos:
        if h.get("pieza_hoy") or (
            h.get("dias_hasta") is not None and 0 <= h["dias_hasta"] <= 60
        ):
            if _prio(h)[0] <= 5:
                return h
    return candidatos[0] if candidatos else None


def construir_plan_marketing(
    *,
    db: Any | None = None,
    dias: int = 365,
    anio: int | None = None,
    mes: int | None = None,
    desarrollar_completo: bool = False,
) -> dict[str, Any]:
    from backend.services.calendario_importante_service import listar_importantes

    hoy = date.today()
    anio = anio or hoy.year
    inicio = date(anio, 1, 1) if anio != hoy.year else hoy
    if inicio < hoy:
        inicio = hoy
    fin_anio = date(anio, 12, 31)
    hasta = min(hoy + timedelta(days=dias), fin_anio)

    agenda = listar_importantes(desde=inicio, hasta=hasta, solo_confirmados=True, db=db)
    items = agenda.get("items", [])

    hitos = _construir_hitos(
        items,
        hoy,
        desarrollar_todas_piezas=desarrollar_completo,
        db=db,
    )
    campaña_activa = _elegir_campaña_activa(hitos, hoy)
    meses = _agrupar_por_mes(hitos, anio)

    plan_hoy = planificar_dia(hoy, db=db)
    if campaña_activa:
        for h in hitos:
            if h["id"] != campaña_activa.get("id"):
                continue
            item_src = {
                "nombre": h["nombre"],
                "tipo": h["tipo"],
                "fecha_inicio": h["fecha_inicio"],
                "fecha_fin": h["fecha_fin"],
                "copy_hook": "",
            }
            nuevas = []
            for p in h.get("piezas", []):
                if p.get("estado") in ("hoy", "proxima") and not p.get("desarrollado"):
                    nuevas.append(desarrollar_pieza(item_src, p, db=db))
                else:
                    nuevas.append(p)
            h["piezas"] = nuevas
            h["pieza_hoy"] = next((p for p in nuevas if p.get("estado") == "hoy"), None)
            h["pieza_proxima"] = next((p for p in nuevas if p.get("estado") == "proxima"), None)
            campaña_activa = h
            break

    resultado = {
        "generado": hoy.isoformat(),
        "anio": anio,
        "desde": inicio.isoformat(),
        "hasta": hasta.isoformat(),
        "filtro_eventos": "Máximo 60 km desde Bialet Massé (tabla + mapas OpenStreetMap)",
        "resumen": {
            "hitos_total": len(hitos),
            "hitos_alta": sum(1 for h in hitos if h["intensidad"] == "alta"),
            "campaña_activa_nombre": (campaña_activa or {}).get("nombre"),
        },
        "campaña_activa": campaña_activa,
        "meses": meses,
        "hitos": hitos,
        "plan_editorial_hoy": _plan_hoy_enriquecido(
            plan_hoy, campaña_activa, (campaña_activa or {}).get("pieza_hoy")
        ),
        "ritmo_semana_sin_hito": _ritmo_semana(hoy),
    }

    if mes and 1 <= mes <= 12:
        resultado["mes_actual"] = next((m for m in meses if m["mes"] == mes), None)
        resultado["hitos_mes"] = resultado["mes_actual"]["hitos"] if resultado["mes_actual"] else []

    return resultado


def _plan_hoy_enriquecido(
    plan_hoy: dict,
    campaña: dict | None,
    pieza_campaña: dict | None,
) -> dict:
    base = {
        "titulo": plan_hoy.get("titulo"),
        "razon": plan_hoy.get("razon"),
        "objetivo": plan_hoy.get("objetivo"),
        "tipo_pieza_label": _TIPO_PIEZA.get(
            _map_objetivo_tipo(plan_hoy.get("objetivo", "")), "Pieza del día"
        ),
        "copy_preview": (plan_hoy.get("copy") or "")[:400],
    }
    if pieza_campaña and pieza_campaña.get("desarrollado"):
        base["desde_campaña"] = campaña.get("nombre") if campaña else None
        base["titulo"] = pieza_campaña.get("titulo_publicacion")
        base["copy_preview"] = pieza_campaña.get("copy_instagram", "")[:500]
        base["guion_resumen"] = pieza_campaña.get("guion", {}).get("hook")
        base["pieza_id"] = pieza_campaña.get("id")
        base["fecha_publicacion"] = pieza_campaña.get("fecha_legible")
    return base


def obtener_hito(hito_id: str, *, db: Any | None = None, desarrollar: bool = True) -> dict | None:
    plan = construir_plan_marketing(db=db, dias=365, desarrollar_completo=desarrollar)
    for h in plan.get("hitos", []):
        if h["id"] == hito_id:
            if desarrollar:
                for i, p in enumerate(h.get("piezas", [])):
                    if not p.get("desarrollado"):
                        item = {
                            "nombre": h["nombre"],
                            "tipo": h["tipo"],
                            "fecha_inicio": h["fecha_inicio"],
                            "copy_hook": "",
                        }
                        h["piezas"][i] = desarrollar_pieza(item, p, db=db)
            return h
    return None


def obtener_pieza(hito_id: str, pieza_id: str, *, db: Any | None = None) -> dict | None:
    h = obtener_hito(hito_id, db=db, desarrollar=True)
    if not h:
        return None
    for p in h.get("piezas", []):
        if p.get("id") == pieza_id:
            if not p.get("desarrollado"):
                item = {"nombre": h["nombre"], "tipo": h["tipo"], "fecha_inicio": h["fecha_inicio"]}
                return desarrollar_pieza(item, p, db=db)
            return p
    return None


def _map_objetivo_tipo(objetivo: str) -> str:
    m = {
        "cta_reserva": "promo_cta",
        "fidelizacion": "emocional_tema",
        "utilidad": "utilidad",
        "branding": "reflexivo_marca",
    }
    return m.get(objetivo, "reflexivo_marca")


def _ritmo_semana(hoy: date) -> list[dict]:
    _dias = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")
    filas = []
    for i in range(7):
        d = hoy + timedelta(days=i)
        p = planificar_dia(d)
        filas.append(
            {
                "dia": _dias[d.weekday()],
                "fecha": d.isoformat(),
                "foco": p.get("titulo") or p.get("razon", "")[:60],
                "tipo": _TIPO_PIEZA.get(_map_objetivo_tipo(p.get("objetivo", "")), ""),
            }
        )
    return filas


def sincronizar_plan_cache(*, db: Any | None = None, anio: int | None = None) -> dict:
    import json
    from pathlib import Path

    plan = construir_plan_marketing(
        db=db, dias=365, anio=anio or date.today().year, desarrollar_completo=False
    )
    path = Path(__file__).resolve().parent.parent / "data" / "plan_marketing_anual.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "archivo": str(path.name),
        "hitos": plan["resumen"]["hitos_total"],
        "anio": plan["anio"],
    }
