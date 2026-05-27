# Workflow video: fotos locales + YouTube

## Pipeline MVP (hoy)

```
media_picker.armar_assets()
    → fotos en archivos multimedia/
    → clips YouTube (turismo_contenidos) si hay DB
    → guion con escenas
    → (opcional) crear_slideshow() MoviePy
    → dueño publica manual
```

## Fotos locales

- Carpeta base: `archivos multimedia/fotos terra natura/`
- Mapeo por ángulo en `calendario_editorial_reglas.json`
- Inventario detallado: `docs/MEDIA_INVENTARIO.md`

**Reglas:**
- Preferir luz natural, horizonte nivelado
- Alpinas: destacar PA matrimonial + balcón en piezas parejas
- No mezclar fotos de otras cabañas/stock

## Videos editoriales automáticos (recomendado)

**Módulo:** `ama/video/editorial_reel_builder.py` + `ama/video/youtube_broll.py`

- **B-roll YouTube** — fragmentos de río, lago, sierras (biblioteca BD + yt-dlp)
- **Fotos propias** — cabañas, parque, pileta (Ken Burns + marca)
- **Montaje** — segmentos encadenados con fundidos, subtítulos, música
- Ver detalle: `docs/BROLL_YOUTUBE_MONTAJE.md`

**Comandos:**
- `local/Generar-videos-editoriales.bat` — hasta 5 videos del calendario
- Panel `/marketing` → «Crear videos (5)» o «Generar video» en cada reel
- API: `POST /api/ama/video/editorial` · `POST /api/ama/video/lote-calendario`

**Salida:** `ama/output/videos/editorial/` y copia en `archivos multimedia/videos marketing/editorial/`

## YouTube (solo referencia / ideas)

1. Ejecutar `local/Recolectar-videos-YouTube.bat` para inspiración de temas
2. Los clips **no** se pegan encima de fotos — el reel editorial es 100 % marca propia

## MoviePy (automático)

```bash
pip install moviepy
POST /api/ama/video/slideshow
```

Parámetros: `carpeta_media`, títulos. Salida: `ama/output/videos/`.

Si falla: usar `brief_canva` del response.

## Canva (manual gratis)

1. Abrir brief del post en calendario
2. Importar fotos listadas en `assets.fotos`
3. Plantilla reel 9:16
4. Exportar MP4 → publicar

## Mezcla foto + YouTube en CapCut (recomendado calidad senior)

1. Importar 2–3 fotos + 1 clip YouTube muteado
2. Aplicar guion `escenas` como storyboard
3. Subtítulos auto + corrección color
4. Export 1080×1920

## Nomenclatura archivos export

`TN_2026-05-25_IG_reel_carnaval_v1.mp4`

## Próximo nivel (V2)

- Render batch desde guion JSON
- Biblioteca música local licenciada
- Auto-subtítulos Whisper local
