@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Videos Terra Natura: B-roll YouTube + fotos del complejo
echo Requiere: ffmpeg + yt-dlp + fotos en "archivos multimedia"
echo Instalar: pip install yt-dlp
echo Musica opcional: ama\assets\music\musica_fondo.mp3
echo.
python -c "from backend.config.database import init_db; init_db(); from ama.video.editorial_reel_builder import build_lote_calendario; import json; r=build_lote_calendario(dias=14,max_videos=5); print(json.dumps(r, ensure_ascii=False, indent=2))"
echo.
echo Videos en: archivos multimedia\videos marketing\editorial\
pause
