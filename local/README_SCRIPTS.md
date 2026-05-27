# Scripts locales — Terra Natura

## Programa unificado (recomendado)

Todo está **dentro del mismo programa** (servidor + navegador). No hace falta abrir muchos `.bat` sueltos.

### 1. Icono en el escritorio (una sola vez)

Doble clic en:

**`local\Crear-icono-escritorio.bat`**

Crea en el escritorio: **«Terra Natura»**

### 2. Usar el programa cada día

Doble clic en **«Terra Natura»** del escritorio.

- Se abre una ventana **«Terra Natura — no cerrar»** (el servidor). Dejala abierta.
- Se abre el navegador en **`/programa`** con tres botones grandes:
  1. **Recolectar videos YouTube** (biblioteca B-roll)
  2. **Calendario 90 días**
  3. **Generar videos editoriales**

También podés entrar a Marketing, Agentes, Turismo y Panel desde el mismo menú.

### URL directa

`http://127.0.0.1:8000/programa`

---

## Scripts sueltos (opcional, mismo motor)

| Archivo | Qué hace |
|---------|----------|
| `Abrir-Terra-Natura.bat` | Igual que el icono del escritorio |
| `Recolectar-videos-YouTube.bat` | Paso 1 sin navegador |
| `Generar-calendario-90-dias.bat` | Paso 2 sin navegador |
| `Generar-videos-editoriales.bat` | Paso 3 sin navegador |
| `inicia_servidor_interno.bat` | Solo servidor (ventana negra) |

---

## Requisitos

- Python 3.11+
- `pip install -r backend/requirements.txt`
- **ffmpeg** en PATH
- **yt-dlp** (`pip install yt-dlp`)
- `.env` con `YOUTUBE_API_KEY` para recolectar YouTube

---

## Videos Kempes (aparte)

`Generar-video-Kempes-Belgrano.bat` — campañas fútbol, no es el flujo editorial de redes.
