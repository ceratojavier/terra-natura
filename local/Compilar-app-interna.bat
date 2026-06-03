@echo off
REM Compila la interfaz React (frontend/app) para que /app/programa funcione.

setlocal EnableExtensions
chcp 65001 >nul
pushd "%~dp0..\frontend\app" >nul

where npm >nul 2>&1
if errorlevel 1 (
  echo No se encuentra npm. Instalá Node.js LTS desde https://nodejs.org
  popd >nul
  pause
  exit /b 1
)

if not exist "node_modules\" (
  echo Instalando dependencias npm...
  call npm install
  if errorlevel 1 goto ERROR
)

echo Compilando app operativa Terra Natura...
call npm run build
if errorlevel 1 goto ERROR

echo Listo: frontend\app\dist
echo.
echo Compilando Video Pro Creator...
call "%~dp0Compilar-video-pro.bat"
popd >nul
exit /b %ERRORLEVEL%

:ERROR
popd >nul
pause
exit /b 1
