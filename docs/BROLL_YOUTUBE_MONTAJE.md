# B-roll YouTube + montaje Terra Natura

## Concepto correcto

YouTube es una **biblioteca de recursos** (río, lago, sierras, Bialet, etc.). El sistema:

1. **Busca** el video (BD turismo o API YouTube con `YOUTUBE_API_KEY`)
2. **Descarga** con `yt-dlp` y cachea en `ama/output/broll_cache/`
3. **Extrae** un fragmento corto (4–5 s), recorte vertical 1080×1920, color suave, fundidos
4. **Alterna** con **fotos propias** del complejo (Ken Burns + textos marca)
5. **Cierra** con tarjeta CTA + subtítulos + música local

No es “pegar YouTube con una foto encima”: es un reel con ritmo narrativo.

## Secuencia por objetivo (ejemplo CTA)

| Orden | Tipo | Ejemplo |
|-------|------|---------|
| 1 | Tarjeta gancho | Texto emocional |
| 2 | B-roll | Río / agua (YouTube) |
| 3 | Foto | Cabaña / parque |
| 4 | B-roll | Lago / dique |
| 5 | Foto | Pileta / vista |
| 6 | Cierre | WhatsApp |

## Requisitos técnicos

```bash
pip install yt-dlp Pillow
```

- **ffmpeg** en PATH  
- **YOUTUBE_API_KEY** en `.env` (búsqueda si falta id en cache)  
- Fotos en `archivos multimedia/`  
- Música opcional: `ama/assets/music/musica_fondo.mp3`

## Comandos

- `local/Recolectar-videos-YouTube.bat` — llena biblioteca en BD  
- `local/Generar-videos-editoriales.bat` — arma hasta 5 videos  
- Panel `/marketing` → Crear videos (5) o Generar video por post

## Código

- `ama/video/youtube_broll.py` — descarga y fragmentos  
- `ama/engine/broll_queries.py` — qué buscar por escena  
- `ama/video/editorial_reel_builder.py` — montaje final  

## Legal

Usar fragmentos cortos con fines promocionales del destino; preferir videos turísticos/genéricos de entorno. Revisar el clip antes de publicar.
