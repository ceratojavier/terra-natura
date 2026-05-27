@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Generando video BELGRANO - Kempes - Bialet Masse...
python -m ama.video.audit_calidad
python -m ama.video.pro_reel_belgrano
if errorlevel 1 pause
echo.
echo Video PRO en: ama\output\videos\kempes_belgrano_PRO_whatsapp.mp4
echo Informe calidad: ama\output\videos\CALIDAD_FOTOS_INFORME.txt
echo Texto en: ama\output\videos\TEXTO_WHATSAPP_KEMPES_BELGRANO.txt
explorer "ama\output\videos"
pause
