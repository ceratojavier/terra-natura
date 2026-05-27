"""
Asistente de configuración Terra Natura — pasos, estado y persistencia local.
Los datos del dueño van a local/config-dueño.json (no commitear).
"""
from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _REPO / "local" / "config-dueño.json"
_UPLOADS_ROOT = _REPO / "local" / "setup-uploads"
_MEDIA_FOTOS = _REPO / "archivos multimedia" / "fotos terra natura"
_MUSIC = _REPO / "ama" / "assets" / "music" / "musica_fondo.mp3"
_ENV_PATH = _REPO / ".env"
_EVENTOS_CONFIRMADOS = _REPO / "ama" / "data" / "eventos_confirmados_ar.json"
_EVENTOS_CORDOBA = _REPO / "ama" / "data" / "eventos_cordoba_turismo_sync.json"

STEPS: list[dict[str, Any]] = [
    {
        "id": "intro",
        "titulo": "Bienvenida",
        "subtitulo": "Configurador Terra Natura",
        "tipo": "info",
        "obligatorio": False,
    },
    {
        "id": "negocio",
        "titulo": "Datos del complejo",
        "subtitulo": "Contacto y ubicación",
        "tipo": "form",
        "obligatorio": True,
        "campos": [
            {"key": "nombre_comercial", "label": "Nombre comercial", "tipo": "text", "default": "Cabañas Alpinas Terra Natura"},
            {"key": "direccion", "label": "Dirección", "tipo": "text", "default": "Los Talas 759, Bialet Massé, Córdoba"},
            {"key": "whatsapp", "label": "WhatsApp reservas (con código país)", "tipo": "tel", "placeholder": "+549351..."},
            {"key": "email", "label": "Email público", "tipo": "email", "placeholder": "terranaturaalpinas@gmail.com"},
        ],
    },
    {
        "id": "objetivos",
        "titulo": "Objetivos de marketing",
        "subtitulo": "Podés marcar varios — ordená por importancia mental",
        "tipo": "form",
        "obligatorio": True,
        "campos": [
            {"key": "obj_reservas_directas", "label": "Más reservas directas (web/WhatsApp)", "tipo": "checkbox"},
            {"key": "obj_ocupacion", "label": "Subir ocupación (alta, baja, puentes)", "tipo": "checkbox"},
            {"key": "obj_parejas", "label": "Más parejas", "tipo": "checkbox"},
            {"key": "obj_familias", "label": "Más familias con niños", "tipo": "checkbox"},
            {"key": "obj_marca", "label": "Marca (IG, reseñas Google)", "tipo": "checkbox"},
            {"key": "obj_eventos", "label": "Llenar por eventos / fines de semana largos", "tipo": "checkbox"},
            {"key": "descripcion_una_frase", "label": "En una frase: qué vendés y a quién", "tipo": "textarea"},
            {"key": "ocupacion_actual", "label": "Ocupación aprox. hoy (%)", "tipo": "text", "placeholder": "ej. 45"},
            {"key": "seguidores_ig", "label": "Seguidores Instagram hoy", "tipo": "text"},
        ],
    },
    {
        "id": "precios",
        "titulo": "Tarifas base + inflación variable (ARS)",
        "subtitulo": "Precio del último verano (sin inflación). El sistema calcula un coeficiente distinto por mes (junio ≠ julio ≠ enero) vía REM.",
        "tipo": "form",
        "obligatorio": True,
        "campos": [
            {
                "key": "base_verano_prom_alpina",
                "label": "Alpina — precio promedio último verano (ARS / noche)",
                "tipo": "number",
            },
            {
                "key": "base_verano_prom_suite",
                "label": "Suite — precio promedio último verano (ARS / noche)",
                "tipo": "number",
            },
            {
                "key": "porcentaje_baja_sobre_verano_alpina",
                "label": "Temporada baja Alpina: % de verano (ej. 0.75 = -25%)",
                "tipo": "number",
                "placeholder": "ej. 0.75",
            },
            {
                "key": "porcentaje_baja_sobre_verano_suite",
                "label": "Temporada baja Suite: % de verano (ej. 0.75 = -25%)",
                "tipo": "number",
                "placeholder": "ej. 0.75",
            },
        ],
    },
    {
        "id": "voz_marca",
        "titulo": "Voz de marca",
        "subtitulo": "Lo que la IA debe decir (y lo que no)",
        "tipo": "form",
        "obligatorio": True,
        "campos": [
            {"key": "frase_negocio", "label": "Frase del negocio (bio, anuncios)", "tipo": "textarea",
             "placeholder": "Escapada a las sierras en Bialet Massé — pileta, 600 m del lago."},
            {"key": "prohibido_punilla", "label": "No usar «Punilla» / «Valle de Punilla» en redes", "tipo": "checkbox", "default": True},
            {"key": "tono_calido", "label": "Tono cálido (vos)", "tipo": "checkbox", "default": True},
            {"key": "ejemplo_mensaje_huesped", "label": "Ejemplo de mensaje que te gustaría enviar", "tipo": "textarea"},
        ],
    },
    {
        "id": "instagram",
        "titulo": "Instagram y redes",
        "subtitulo": "Perfil y link en bio",
        "tipo": "form",
        "obligatorio": True,
        "campos": [
            {"key": "usuario_ig", "label": "Usuario Instagram (sin @)", "tipo": "text", "placeholder": "terranaturabialet"},
            {"key": "bio_borrador", "label": "Bio (borrador)", "tipo": "textarea"},
            {"key": "url_google_maps", "label": "Link Google Maps del complejo", "tipo": "url"},
            {"key": "url_booking_publico", "label": "Link público Booking (sin contraseña en URL)", "tipo": "url"},
            {"key": "url_facebook", "label": "Facebook Page (opcional)", "tipo": "url"},
        ],
    },
    {
        "id": "fotos",
        "titulo": "Fotos y videos",
        "subtitulo": "Subí archivos o copiá a la carpeta del proyecto",
        "tipo": "upload",
        "obligatorio": True,
        "acepta": "image/*,video/*",
    },
    {
        "id": "herramientas",
        "titulo": "Herramientas en tu PC",
        "subtitulo": "Python, ffmpeg, yt-dlp, música de fondo",
        "tipo": "checklist_auto",
        "obligatorio": True,
    },
    {
        "id": "youtube",
        "titulo": "YouTube API (B-roll)",
        "subtitulo": "Para recolectar videos de sierras / lago",
        "tipo": "form",
        "obligatorio": False,
        "campos": [
            {"key": "youtube_api_key", "label": "YOUTUBE_API_KEY (se guarda solo en tu PC)", "tipo": "password"},
            {"key": "youtube_omitir", "label": "Configurar más adelante", "tipo": "checkbox"},
        ],
    },
    {
        "id": "canales",
        "titulo": "Canales de reserva",
        "subtitulo": "Un enlace iCal por unidad en Booking, Airbnb u otra OTA",
        "tipo": "ical_canales",
        "obligatorio": True,
    },
    {
        "id": "eventos",
        "titulo": "Agenda de eventos",
        "subtitulo": "Elegí fuentes: Córdoba Turismo, Punilla, deportes, Kempes, Cosquín…",
        "tipo": "fuentes_eventos",
        "obligatorio": False,
    },
    {
        "id": "apis",
        "titulo": "APIs opcionales",
        "subtitulo": "Meta, WhatsApp Cloud, Mercado Pago — podés saltar",
        "tipo": "form",
        "obligatorio": False,
        "campos": [
            {"key": "meta_configurado", "label": "Ya tengo app Meta / token de página", "tipo": "checkbox"},
            {"key": "whatsapp_cloud", "label": "WhatsApp Business API conectada", "tipo": "checkbox"},
            {"key": "mercadopago", "label": "Mercado Pago listo para cobrar", "tipo": "checkbox"},
            {"key": "notas_apis", "label": "Notas", "tipo": "textarea"},
        ],
    },
    {
        "id": "resumen",
        "titulo": "Resumen",
        "subtitulo": "Qué falta y enlaces útiles",
        "tipo": "resumen",
        "obligatorio": False,
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_raw() -> dict[str, Any]:
    if not _CONFIG_PATH.is_file():
        return {
            "version": 1,
            "creado": _utc_now(),
            "actualizado": _utc_now(),
            "paso_actual": "intro",
            "completados": [],
            "datos": {},
            "adjuntos": {},
        }
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "paso_actual": "intro", "completados": [], "datos": {}, "adjuntos": {}}


def _save_raw(data: dict[str, Any]) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["actualizado"] = _utc_now()
    _CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_step_def(step_id: str) -> dict[str, Any] | None:
    for s in STEPS:
        if s["id"] == step_id:
            return s
    return None


def list_steps() -> list[dict[str, Any]]:
    return STEPS


def _env_has(key: str) -> bool:
    if _ENV_PATH.is_file():
        text = _ENV_PATH.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            if line.strip().startswith(f"{key}=") and "=" in line:
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and val.lower() not in ("", "changeme", "cambiar-en-produccion"):
                    return True
    return bool(os.environ.get(key, "").strip())


_MEDIA_EXTS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".mov", ".m4v"})


def _es_archivo_media(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in _MEDIA_EXTS


def _inventario_fotos() -> dict[str, Any]:
    """
    Cuenta fotos/videos en fotos terra natura/** (subcarpetas incluidas).
    Los 7 PNG sueltos en la raíz (capturas Google/API) se reportan aparte.
    """
    total = 0
    en_raiz = 0
    por_carpeta: dict[str, int] = {}
    carpetas: list[str] = []

    if _MEDIA_FOTOS.is_dir():
        for item in sorted(_MEDIA_FOTOS.iterdir()):
            if item.is_dir():
                carpetas.append(item.name)
                n = sum(1 for f in item.rglob("*") if _es_archivo_media(f))
                por_carpeta[item.name] = n
                total += n
            elif _es_archivo_media(item):
                en_raiz += 1
                total += 1

    subidos = 0
    uploads = _UPLOADS_ROOT / "fotos"
    if uploads.is_dir():
        subidos = sum(1 for f in uploads.rglob("*") if _es_archivo_media(f))

    return {
        "total": total + subidos,
        "en_carpetas": total - en_raiz,
        "en_raiz": en_raiz,
        "subidos_wizard": subidos,
        "carpetas": carpetas,
        "por_carpeta": por_carpeta,
        "ruta": str(_MEDIA_FOTOS.relative_to(_REPO)).replace("\\", "/"),
    }


def _count_fotos() -> int:
    return int(_inventario_fotos().get("total", 0))


def _check_herramientas() -> dict[str, bool]:
    return {
        "python": bool(shutil.which("python") or shutil.which("py")),
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "yt_dlp": bool(shutil.which("yt-dlp")),
        "musica_fondo": _MUSIC.is_file(),
    }


def _normalize_precios(d: dict[str, Any]) -> dict[str, Any]:
    """
    Compatibilidad: si el usuario ya cargó el paso 4 con el formato viejo
    (precio_alpina_baja_noche, precio_alpina_alta_noche, etc.), lo convertimos
    al nuevo modelo (base verano + % baja).

    Nota: si no tenemos inflación histórica, inicializamos inflación en 0%
    (el valor 'alta' viejo pasa a ser 'base verano' nuevo).
    """
    if not isinstance(d, dict):
        return {}

    if "base_verano_prom_alpina" in d:
        return d

    # formato viejo
    needed_old = [
        "precio_alpina_alta_noche",
        "precio_alpina_baja_noche",
        "precio_suite_alta_noche",
        "precio_suite_baja_noche",
    ]
    if not all(k in d for k in needed_old):
        return d

    try:
        alta_alp = float(d.get("precio_alpina_alta_noche") or 0)
        baja_alp = float(d.get("precio_alpina_baja_noche") or 0)
        alta_su = float(d.get("precio_suite_alta_noche") or 0)
        baja_su = float(d.get("precio_suite_baja_noche") or 0)
    except Exception:
        return d

    out = dict(d)
    out["base_verano_prom_alpina"] = alta_alp
    out["base_verano_prom_suite"] = alta_su
    out["porcentaje_baja_sobre_verano_alpina"] = (baja_alp / alta_alp) if alta_alp > 0 else None
    out["porcentaje_baja_sobre_verano_suite"] = (baja_su / alta_su) if alta_su > 0 else None
    return out


def _check_step(step_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Estado: ok | parcial | pendiente + mensaje + ayuda."""
    d = data.get("datos", {}).get(step_id, {}) or {}
    adj = data.get("adjuntos", {}).get(step_id, []) or []

    if step_id == "intro":
        return {"estado": "ok", "mensaje": "Listo para empezar."}

    if step_id == "negocio":
        ok = bool((d.get("whatsapp") or "").strip())
        return {
            "estado": "ok" if ok else "pendiente",
            "mensaje": "WhatsApp de reservas cargado." if ok else "Falta WhatsApp de reservas.",
        }

    if step_id == "objetivos":
        keys = [k for k in d if k.startswith("obj_") and d.get(k)]
        ok = len(keys) >= 1 and bool((d.get("descripcion_una_frase") or "").strip())
        return {
            "estado": "ok" if ok else "parcial" if keys else "pendiente",
            "mensaje": "Objetivos y frase definidos." if ok else "Marcá al menos un objetivo y la frase del negocio.",
        }

    if step_id == "precios":
        required = [
            "base_verano_prom_alpina",
            "base_verano_prom_suite",
            "porcentaje_baja_sobre_verano_alpina",
            "porcentaje_baja_sobre_verano_suite",
        ]
        d_norm = _normalize_precios(d)
        ok = all(str(d_norm.get(k, "")).strip() != "" for k in required)
        return {
            "estado": "ok" if ok else "pendiente" if not d else "parcial",
            "mensaje": (
                "Base verano y % baja cargados. Coeficiente inflación se calcula por fecha al cotizar."
                if ok
                else "Completá precio base del último verano y % temporada baja."
            ),
        }

    if step_id == "voz_marca":
        ok = bool((d.get("frase_negocio") or "").strip())
        return {
            "estado": "ok" if ok else "pendiente",
            "mensaje": "Voz de marca definida." if ok else "Falta la frase del negocio.",
        }

    if step_id == "instagram":
        ok = bool((d.get("usuario_ig") or "").strip())
        return {
            "estado": "ok" if ok else "pendiente",
            "mensaje": "Usuario IG cargado." if ok else "Falta usuario de Instagram.",
        }

    if step_id == "fotos":
        inv = _inventario_fotos()
        n = inv["total"]
        en_carp = inv["en_carpetas"]
        ok = en_carp >= 3 or len(adj) >= 3
        return {
            "estado": "ok" if ok else "parcial" if n or adj else "pendiente",
            "mensaje": (
                f"{en_carp} fotos/videos en {len(inv['carpetas'])} carpetas"
                f" (+{inv['en_raiz']} en raíz, +{len(adj)} subidos acá). Listo para videos."
                if ok
                else f"{en_carp} en carpetas — recomendado ≥3 en PILETA/PARQUE/cabañas."
            ),
            "detalle": inv,
        }

    if step_id == "herramientas":
        h = _check_herramientas()
        ok = all(h.values())
        faltan = [k for k, v in h.items() if not v]
        return {
            "estado": "ok" if ok else "parcial",
            "mensaje": "Todas las herramientas OK." if ok else f"Falta: {', '.join(faltan)}",
            "detalle": h,
        }

    if step_id == "youtube":
        if d.get("youtube_omitir"):
            return {"estado": "parcial", "mensaje": "Omitido — podés activar después."}
        key = (d.get("youtube_api_key") or "").strip() or (
            _env_has("YOUTUBE_API_KEY") and "***"
        )
        ok = bool(key)
        return {
            "estado": "ok" if ok else "pendiente",
            "mensaje": "API YouTube configurada." if ok else "Sin API — el paso 1 del programa no descargará B-roll.",
        }

    if step_id == "canales":
        from backend.services.ical_feeds_service import check_canales, normalize_canales

        return check_canales(normalize_canales(d))

    if step_id == "eventos":
        from backend.services.fuentes_eventos_service import check_eventos, normalize_eventos

        return check_eventos(normalize_eventos(d))

    if step_id == "apis":
        return {"estado": "parcial", "mensaje": "Opcional — publicación automática aún no conectada."}

    if step_id == "resumen":
        return {"estado": "ok", "mensaje": "Revisá el checklist."}

    return {"estado": "pendiente", "mensaje": ""}


def get_instrucciones(step_id: str) -> list[dict[str, str]]:
    """Pasos «cómo conseguir» para el dueño."""
    guias: dict[str, list[dict[str, str]]] = {
        "negocio": [
            {"titulo": "WhatsApp", "texto": "Usá el número que ya atendés huéspedes. Formato internacional: +549351xxxxxxx (sin espacios)."},
        ],
        "precios": [
            {
                "titulo": "Coeficiente variable (no es un % fijo)",
                "texto": "Puente de junio, vacaciones de julio y verano de enero tienen coeficientes distintos. Se calcula inflación acumulada del mismo mes del año pasado hasta la fecha (REM mensual).",
            },
            {
                "titulo": "Vos solo cargás",
                "texto": "Precio promedio del último verano (sin inflación) y % de temporada baja sobre ese precio ya ajustado por mes.",
            },
            {
                "titulo": "Actualizar REM",
                "texto": "Botón «Actualizar serie REM» — descarga tasas mensuales de consultoras (BCRA).",
            },
        ],
        "youtube": [
            {"titulo": "1. Entrá a Google Cloud Console", "texto": "https://console.cloud.google.com/ → Crear proyecto «Terra Natura»."},
            {"titulo": "2. Habilitar YouTube Data API v3", "texto": "APIs y servicios → Biblioteca → buscar «YouTube Data API v3» → Habilitar."},
            {"titulo": "3. Crear clave API", "texto": "Credenciales → Crear credenciales → Clave API. Copiala y pegala acá (solo se guarda en local/config-dueño.json)."},
            {"titulo": "4. Pegar en .env (opcional)", "texto": "En la raíz del proyecto, archivo .env: YOUTUBE_API_KEY=tu_clave"},
            {"titulo": "Documentación", "texto": "Ver docs/YOUTUBE_API_SETUP.md en el proyecto si existe."},
        ],
        "fotos": [
            {
                "titulo": "Carpetas que ya tenés",
                "texto": "El sistema cuenta fotos en todas las subcarpetas (Alpinas, Suites, PILETA, PARQUE, etc.). No hace falta moverlas.",
            },
            {"titulo": "Ruta", "texto": "archivos multimedia/fotos terra natura/"},
            {
                "titulo": "PNG en la raíz",
                "texto": "Las capturas GOOGLE/API sueltas en la raíz no son fotos del complejo; las útiles están en las subcarpetas.",
            },
        ],
        "herramientas": [
            {"titulo": "ffmpeg", "texto": "En PowerShell (admin): winget install Gyan.FFmpeg — o descargá desde ffmpeg.org y agregá al PATH."},
            {"titulo": "yt-dlp", "texto": "winget install yt-dlp  — o: pip install yt-dlp"},
            {"titulo": "Música", "texto": "Si falta musica_fondo.mp3, ejecutá local/Descargar-musica-fondo.bat (si existe) o copiá un MP3 libre a ama/assets/music/"},
        ],
        "instagram": [
            {"titulo": "Usuario", "texto": "El @ que querés usar. Si aún no existe la cuenta, dejá el nombre deseado y crealo después."},
            {"titulo": "Bio", "texto": "Copiá el borrador de marketing/contexto/FEED_INSTAGRAM_TERRA_NATURA.md o escribí acá."},
            {"titulo": "Google Maps", "texto": "En Google Maps → tu lugar → Compartir → Copiar enlace."},
        ],
        "canales": [
            {
                "titulo": "Booking (varias propiedades)",
                "texto": "En cada anuncio: Calendario → Sincronizar → Exportar calendario → pegá el enlace en la unidad correcta.",
            },
            {
                "titulo": "Airbnb u otra OTA",
                "texto": "Usá «+ Agregar enlace iCal» por unidad. Misma unidad puede tener Booking + Airbnb.",
            },
            {
                "titulo": "Solo directo",
                "texto": "Si marcás «solo reserva directa», el sistema no promociona OTAs en borradores AMA.",
            },
        ],
        "eventos": [
            {
                "titulo": "De dónde salen los eventos",
                "texto": "Datos automáticos: confirmados, calendario importante (Kempes, Cosquín…), fiestas recurrentes, feriados. Web: Córdoba Turismo. Referencia: medios, running, Kempes web (revisás el link).",
            },
            {
                "titulo": "Local Bialet",
                "texto": "Peatonales, carnaval y fiestas del municipio: bialetmasse.com.ar y calendario_importante (eventos_locales_bialet).",
            },
            {
                "titulo": "Sincronizar",
                "texto": "Pulsá «Sincronizar agenda» acá o en /programa. También: local/Actualizar-agenda-eventos.bat cada lunes.",
            },
            {
                "titulo": "Evento manual",
                "texto": "ama/data/eventos_confirmados_ar.json — fecha oficial, estado confirmado.",
            },
        ],
        "apis": [
            {"titulo": "Instagram/Facebook automático", "texto": "Requiere Meta Business + app en developers.facebook.com. Hoy el MVP es copiar desde /marketing."},
            {"titulo": "WhatsApp Cloud", "texto": "Meta Developer → WhatsApp → número de prueba. Ver .env.example WHATSAPP_VERIFY_TOKEN."},
            {"titulo": "Mercado Pago", "texto": "developers.mercadopago.com → credenciales de prueba. Integración PMS en fase posterior."},
        ],
    }
    return guias.get(step_id, [])


def estado_completo() -> dict[str, Any]:
    raw = _load_raw()
    pasos_out = []
    ok_count = 0
    oblig = [s for s in STEPS if s.get("obligatorio") and s["id"] != "resumen"]
    for s in STEPS:
        chk = _check_step(s["id"], raw)
        if chk["estado"] == "ok":
            ok_count += 1
        pasos_out.append({
            "id": s["id"],
            "titulo": s["titulo"],
            "subtitulo": s.get("subtitulo", ""),
            "tipo": s.get("tipo", "form"),
            "obligatorio": s.get("obligatorio", False),
            "estado": chk["estado"],
            "mensaje": chk["mensaje"],
            "completado_manual": s["id"] in raw.get("completados", []),
        })
    pct = round(100 * ok_count / max(len(STEPS) - 1, 1))
    oblig_ok = sum(1 for p in pasos_out if p["obligatorio"] and p["estado"] == "ok")
    return {
        "progreso_pct": pct,
        "paso_actual": raw.get("paso_actual", "intro"),
        "pasos": pasos_out,
        "obligatorios_ok": oblig_ok,
        "obligatorios_total": len(oblig),
        "listo_operar": oblig_ok >= len(oblig) - 1,
        "config_existe": _CONFIG_PATH.is_file(),
        "ruta_config": str(_CONFIG_PATH.relative_to(_REPO)).replace("\\", "/"),
    }


def obtener_paso(step_id: str) -> dict[str, Any]:
    step = get_step_def(step_id)
    if not step:
        raise ValueError(f"Paso desconocido: {step_id}")
    raw = _load_raw()
    chk = _check_step(step_id, raw)
    valores = raw.get("datos", {}).get(step_id, {}) or {}
    if step_id == "precios":
        valores = _normalize_precios(valores)
    if step_id == "canales":
        from backend.services.ical_feeds_service import (
            PLATAFORMAS_ICAL,
            UNIDADES_ICAL,
            normalize_canales,
        )

        valores = normalize_canales(valores)

    if step_id == "eventos":
        from backend.services.fuentes_eventos_service import normalize_eventos

        valores = normalize_eventos(valores)
    inventario_fotos = None
    if step_id == "fotos":
        inventario_fotos = _inventario_fotos()

    vista_coeficientes = None
    if step_id == "precios":
        try:
            from backend.services.inflacion_coeficiente_service import (
                actualizar_serie_rem,
                vista_previa_periodos,
            )

            actualizar_serie_rem(forzar=False)
            b_alp = float(valores.get("base_verano_prom_alpina") or 115000)
            b_su = float(valores.get("base_verano_prom_suite") or 87500)
            vista_coeficientes = vista_previa_periodos(b_alp, b_su)
        except Exception:
            vista_coeficientes = None
    unidades_ical = None
    plataformas_ical = None
    if step_id == "canales":
        from backend.services.ical_feeds_service import PLATAFORMAS_ICAL, UNIDADES_ICAL

        unidades_ical = UNIDADES_ICAL
        plataformas_ical = PLATAFORMAS_ICAL

    catalogo_fuentes_eventos = None
    if step_id == "eventos":
        from backend.services.fuentes_eventos_service import resumen_para_ui

        catalogo_fuentes_eventos = resumen_para_ui()
        catalogo_fuentes_eventos["valores"] = valores

    return {
        "paso": step,
        "valores": valores,
        "adjuntos": raw.get("adjuntos", {}).get(step_id, []),
        "check": chk,
        "vista_coeficientes": vista_coeficientes,
        "inventario_fotos": inventario_fotos,
        "unidades_ical": unidades_ical,
        "plataformas_ical": plataformas_ical,
        "catalogo_fuentes_eventos": catalogo_fuentes_eventos,
        "instrucciones": get_instrucciones(step_id),
        "indice": next(i for i, s in enumerate(STEPS) if s["id"] == step_id),
        "total": len(STEPS),
    }


def guardar_paso(step_id: str, valores: dict[str, Any], marcar_completo: bool = True) -> dict[str, Any]:
    step = get_step_def(step_id)
    if not step:
        raise ValueError(f"Paso desconocido: {step_id}")

    raw = _load_raw()
    merged = {**raw.get("datos", {}).get(step_id, {}), **valores}
    if step_id == "canales":
        from backend.services.ical_feeds_service import normalize_canales

        merged = normalize_canales(merged)
    raw.setdefault("datos", {})[step_id] = merged
    raw["paso_actual"] = step_id
    if marcar_completo and step_id not in raw.get("completados", []):
        raw.setdefault("completados", []).append(step_id)

    if step_id == "precios":
        _sync_precios_db(_normalize_precios(raw["datos"].get("precios", {})))

    _sync_archivos_marketing(step_id, raw["datos"].get(step_id, {}))
    if step_id == "canales":
        _sync_canales_db(raw["datos"]["canales"])
    if step_id == "eventos":
        from backend.services.fuentes_eventos_service import guardar_runtime_config

        guardar_runtime_config(raw["datos"]["eventos"])
    if step_id == "youtube" and valores.get("youtube_api_key"):
        _sync_env_youtube(valores["youtube_api_key"])

    _save_raw(raw)
    return {"ok": True, "check": _check_step(step_id, raw)}


def _sync_env_youtube(api_key: str) -> None:
    """Escribe YOUTUBE_API_KEY en .env si no existe línea (solo local)."""
    key = api_key.strip()
    if not key or len(key) < 10:
        return
    lines: list[str] = []
    found = False
    if _ENV_PATH.is_file():
        lines = _ENV_PATH.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("YOUTUBE_API_KEY="):
                lines[i] = f"YOUTUBE_API_KEY={key}"
                found = True
                break
    if not found:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(f"YOUTUBE_API_KEY={key}")
    _ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sync_canales_db(canales: dict[str, Any]) -> None:
    try:
        from backend.config.database import SessionLocal
        from backend.services import config_service
        from backend.services.ical_feeds_service import patch_config_canales

        patch = patch_config_canales(canales)
        if not patch:
            return
        db = SessionLocal()
        try:
            config_service.set_config(db, "canales", patch, merge=True)
            config_service.set_config(db, "config_canales", patch, merge=True)
        finally:
            db.close()
    except Exception:
        pass


def _sync_archivos_marketing(step_id: str, valores: dict[str, Any]) -> None:
    """Escribe JSON/markdown legible para Cursor y agentes."""
    ctx = _REPO / "marketing" / "contexto"
    ctx.mkdir(parents=True, exist_ok=True)

    if step_id == "negocio":
        (ctx / "negocio.json").write_text(
            json.dumps(valores, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if step_id == "objetivos":
        (ctx / "objetivos.json").write_text(
            json.dumps(valores, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if step_id == "voz_marca":
        md = _render_voz_marca_md(valores)
        (_REPO / "marketing" / "contexto" / "00_voz_marca.md").write_text(md, encoding="utf-8")

    if step_id == "instagram":
        (ctx / "redes.json").write_text(
            json.dumps(valores, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if step_id == "canales":
        from backend.services.ical_feeds_service import normalize_canales

        (ctx / "canales_ical.json").write_text(
            json.dumps(normalize_canales(valores), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _render_voz_marca_md(v: dict[str, Any]) -> str:
    frase = (v.get("frase_negocio") or "").strip()
    ej = (v.get("ejemplo_mensaje_huesped") or "").strip()
    no_pun = v.get("prohibido_punilla", True)
    tono = v.get("tono_calido", True)
    return f"""# Voz de marca — formulario dueño

> Generado por el configurador web. Alineá con **`docs/COPY_TONO_MARCA.md`**.

## Frase del negocio (una línea)

> {frase or "(completar en configurador)"}

## Palabras que SÍ querés que use la IA

- escapada a las sierras  
- sierras de Córdoba / sierra cordobesa  
- Bialet Massé  
- lago San Roque / Dique San Roque  
- refugio / desconectar  
- reserva directa / dueños en el predio  

## Palabras que NO (nunca en redes ni WhatsApp comercial)

- [{"x" if no_pun else " "}] Punilla / Valle de Punilla (como marketing)  
- [ ] Barato / low cost  

## Tono (marcá)

- [{"x" if tono else " "}] Cálido, vos  
- [{"x" if tono else " "}] Cordobés suave (sin exagerar lunfardo)  

## Ejemplo de mensaje que te gustaría recibir como huésped

> {ej or "(completar)"}

---

*Actualizado: {_utc_now()[:10]} desde /configurador*
"""


def guardar_adjunto(step_id: str, filename: str, content: bytes) -> dict[str, Any]:
    safe = re.sub(r"[^\w.\-]", "_", filename)[:120]
    folder = _UPLOADS_ROOT / step_id
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / safe
    dest.write_bytes(content)
    rel = str(dest.relative_to(_REPO)).replace("\\", "/")

    raw = _load_raw()
    raw.setdefault("adjuntos", {}).setdefault(step_id, [])
    if rel not in raw["adjuntos"][step_id]:
        raw["adjuntos"][step_id].append(rel)
    _save_raw(raw)
    return {"ok": True, "ruta": rel, "nombre": safe}


def herramientas_detalle() -> dict[str, Any]:
    return _check_herramientas()


def _sync_precios_db(precios: dict[str, Any]) -> None:
    """
    Guarda precios BASE (último verano, sin inflación) y % baja.
    La inflación se aplica al cotizar con coeficiente variable por fecha.
    """
    try:
        from backend.config.database import SessionLocal
        from backend.services import config_service, unidad_service

        db = SessionLocal()
        try:
            b_alp = float(precios.get("base_verano_prom_alpina") or 0)
            b_su = float(precios.get("base_verano_prom_suite") or 0)
            pct_baja_alp = float(precios.get("porcentaje_baja_sobre_verano_alpina") or 0)
            pct_baja_su = float(precios.get("porcentaje_baja_sobre_verano_suite") or 0)

            if b_alp <= 0 or b_su <= 0:
                return

            # Referencia en unidades (lista sin inflación; motor recalcula al cotizar)
            for uid in ("alpina-1", "alpina-2", "alpina-3"):
                unidad_service.update_unidad(
                    db,
                    uid,
                    {"precio_verano_min": b_alp, "precio_verano_max": b_alp},
                )

            for uid in ("suite-4", "suite-5"):
                unidad_service.update_unidad(
                    db,
                    uid,
                    {"precio_verano_min": b_su, "precio_verano_max": b_su},
                )

            cfg = config_service.get_config(db, "tarifas_promociones") or {}
            raw = cfg.get("valor", {}) if isinstance(cfg.get("valor"), dict) else {}
            raw.setdefault("temporada_baja", {})
            if not isinstance(raw.get("temporada_baja"), dict):
                raw["temporada_baja"] = {}

            raw["base_precios"] = {
                "alpina": b_alp,
                "suite": b_su,
                "nota": "Precio último verano sin inflación; coeficiente REM por fecha al cotizar",
            }
            raw["base_verano_prom_alpina"] = b_alp
            raw["base_verano_prom_suite"] = b_su
            raw["porcentaje_baja_sobre_verano_alpina"] = (
                pct_baja_alp if pct_baja_alp > 0 else None
            )
            raw["porcentaje_baja_sobre_verano_suite"] = (
                pct_baja_su if pct_baja_su > 0 else None
            )
            raw["modelo_inflacion"] = "coeficiente_interanual_mismo_mes"

            config_service.set_config(db, "tarifas_promociones", raw, merge=False)
        finally:
            db.close()
    except Exception:
        return
