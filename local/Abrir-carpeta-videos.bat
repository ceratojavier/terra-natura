@echo off
chcp 65001 >nul
cd /d "%~dp0.."
set CARPETA=%cd%\ama\output\videos
if not exist "%CARPETA%" mkdir "%CARPETA%"
explorer "%CARPETA%"
echo.
echo Videos y textos WhatsApp estan en:
echo %CARPETA%
pause
