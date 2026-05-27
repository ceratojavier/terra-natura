# Videos reel armónicos — fotos tuyas + fragmentos YouTube

## Qué pedís

Un reel **agradable de ver**: no “un trozo de YouTube pegado y una foto”, sino **ritmo narrativo** — entorno (agua, sierras, lago) → **tu complejo** (pileta, cabaña, parque) → cierre con marca.

Eso ya está pensado en el código; el montaje usa **fundido cruzado** entre escenas (no corte seco).

---

## Cómo lo arma el sistema (hoy)

| Paso | Qué hace |
|------|----------|
| 1 | **Guion por escenas** — alterna `broll_youtube` y `foto` (ver `ama/engine/broll_queries.py`) |
| 2 | **YouTube** — `yt-dlp` descarga, `ffmpeg` extrae 4–5 s vertical 1080×1920, color suave, fade in/out |
| 3 | **Tus fotos** — Ken Burns (zoom/pan), mismo degradé verde abajo, textos marca |
| 4 | **Unión** — `editorial_reel_builder.py` aplica **xfade ~0,45 s** entre cada escena |
| 5 | **Audio** — música local + subtítulos ASS (voz sugerida en guion) |

**Salida:** `ama/output/videos/editorial/` y copia en `archivos multimedia/videos marketing/editorial/`

**Comandos:**

- `local/Recolectar-videos-YouTube.bat` — biblioteca de IDs en BD  
- `local/Generar-videos-editoriales.bat` — hasta 5 reels del calendario  
- Panel `/marketing` — generar por post  

---

## Herramientas necesarias (cotización)

### Gratis — obligatorias (MVP)

| Herramienta | Para qué | Costo |
|-------------|----------|-------|
| **ffmpeg** | Cortes, vertical, fundidos, música | $0 |
| **yt-dlp** | Descargar fragmentos YouTube | $0 |
| **Python + Pillow** | Fotos animadas, tarjetas marca | $0 |
| **Cursor** (tu plan) | Guiones y ajustes | Ya lo tenés (~USD 20/mes) |
| **YOUTUBE_API_KEY** (opcional) | Buscar B-roll si no hay ID en biblioteca | Gratis con cuota Google |

### Gratis — recomendadas

| Herramienta | Para qué |
|-------------|----------|
| Música **libre de derechos** en `ama/assets/music/` | Evitar strike en IG |
| Fotos clasificadas en `archivos multimedia/` | Ver `docs/MEDIA_INVENTARIO.md` |

### De pago — solo si querés más adelante (no obligatorio)

| Herramienta | Para qué | Orden de magnitud |
|-------------|----------|-------------------|
| **Epidemic Sound / Artlist** | Música premium sin copyright | ~USD 10–15/mes |
| **Canva Pro** | Ajustes manuales puntuales | ~USD 13/mes |
| **CapCut / DaVinci** | Retoque manual de un reel difícil | $0 / $0 |
| **API Meta** publicar reels | Automatizar subida | $0 API; requiere cuenta Business |

**No hace falta** Adobe, Runway ni IA de video de pago para el MVP: el estilo “armónico” sale de **secuencia + fundidos + misma paleta**, no de IA generativa.

---

## Qué necesitás vos (checklist)

1. **ffmpeg** instalado y en PATH (`ffmpeg -version` en PowerShell).  
2. **yt-dlp:** `pip install yt-dlp`  
3. **Fotos** del complejo en `archivos multimedia/` (exterior, pileta, interior, vista).  
4. **Un MP3** de fondo en `ama/assets/music/musica_fondo.mp3` (opcional pero mejora mucho).  
5. Ejecutar **Recolectar videos YouTube** una vez para llenar biblioteca.  
6. Revisar el primer reel generado; si un clip YouTube no sirve, cambiar ID en el post o en BD turismo.

---

## Legal YouTube

Fragmentos **cortos**, turismo/entorno, sin reemplazar tus fotos del producto. Revisá cada clip antes de publicar. Preferir canales oficiales de turismo / drone genérico siempre que se pueda.

---

## Si algo se ve “a saltos”

1. Confirmá **ffmpeg reciente** (xfade entre escenas).  
2. Más fotos propias → menos dependencia de un solo clip YT.  
3. Pedir en Cursor: *“Regenerá el reel del día con secuencia cta_reserva y xfade”*.  
4. Modo 🟡: aprobás el MP4 en `/marketing` antes de subir.

---

## Código principal

- `ama/video/editorial_reel_builder.py` — montaje final  
- `ama/video/youtube_broll.py` — fragmentos  
- `ama/video/brand_frames.py` — fotos + tarjetas  
- `ama/engine/broll_queries.py` — orden narrativo  
