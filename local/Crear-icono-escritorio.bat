@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Creando icono Terra Natura en el escritorio...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Crear-acceso-escritorio.ps1"
echo.
pause
