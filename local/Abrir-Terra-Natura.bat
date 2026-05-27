@echo off

REM Terra Natura — un solo programa (servidor + navegador en /programa)

setlocal EnableExtensions

chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"

pushd "%SCRIPT_DIR%.." >nul



powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1

if errorlevel 1 goto NECESITO_SERVIDOR



start "" "http://127.0.0.1:8000/configurador"

popd >nul

goto FIN



:NECESITO_SERVIDOR

start "Terra Natura — no cerrar esta ventana" cmd /k call "%SCRIPT_DIR%inicia_servidor_interno.bat"

timeout /t 6 /nobreak >nul

start "" "http://127.0.0.1:8000/configurador"

popd >nul



:FIN

endlocal

