@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Calendario editorial 90 dias - Terra Natura
echo Instagram, Facebook, WhatsApp Status, TikTok
echo.
python -m ama.engine.calendar_90_cli
echo.
echo Listo. Abri http://127.0.0.1:8000/marketing y revisa Calendario
pause
