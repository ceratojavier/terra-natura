@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Importando fotos del chat y generando Belgrano + River...
python -m ama.video.generar_videos_kempes
explorer "ama\output\videos"
pause
