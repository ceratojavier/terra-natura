@echo off
chcp 65001 >nul
echo Abriendo Google Cloud para crear la clave de YouTube...
echo Leé: docs\PASO_A_PASO_CLAVE_YOUTUBE.md
start https://console.cloud.google.com/apis/library/youtube.googleapis.com
timeout /t 2 >nul
start https://console.cloud.google.com/apis/credentials
explorer "%~dp0..\docs"
pause
