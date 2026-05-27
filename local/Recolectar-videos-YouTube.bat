@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Necesitas YOUTUBE_API_KEY en el archivo .env
echo Guia: docs\PASO_A_PASO_CLAVE_YOUTUBE.md
echo Si no tenes clave: doble clic en Abrir-pagina-clave-YouTube.bat
echo.
python -m backend.services.youtube_turismo_cli
pause
