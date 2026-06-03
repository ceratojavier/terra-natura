@echo off

REM Terra Natura — icono escritorio: servidor + navegador en /programa

setlocal EnableExtensions

chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "REPO=%SCRIPT_DIR%.."
set "DIST=%REPO%\frontend\app\dist\index.html"
set "DIST_VP=%REPO%\frontend\video-pro-creator\dist\index.html"

pushd "%REPO%" >nul

if not exist "%DIST%" (
  echo Primera vez o falta la interfaz nueva — compilando...
  call "%SCRIPT_DIR%Compilar-app-interna.bat"
)

if not exist "%DIST_VP%" (
  echo Compilando Video Pro Creator...
  call "%SCRIPT_DIR%Compilar-video-pro.bat"
)

set "URL=http://127.0.0.1:8000/app/hoy"

powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1

if errorlevel 1 goto NECESITO_SERVIDOR

start "" "%URL%"
popd >nul
goto FIN

:NECESITO_SERVIDOR
start "Terra Natura — no cerrar esta ventana" cmd /k call "%SCRIPT_DIR%inicia_servidor_interno.bat"

for /l %%I in (1,1,25) do (
  powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
  if not errorlevel 1 goto ABRIR_PROGRAMA
  timeout /t 1 /nobreak >nul
)

:ABRIR_PROGRAMA
start "" "%URL%"

popd >nul

:FIN
endlocal
