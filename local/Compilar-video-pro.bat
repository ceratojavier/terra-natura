@echo off
REM Compila Video Pro Creator (frontend/video-pro-creator) para /video-pro/

setlocal EnableExtensions
chcp 65001 >nul
pushd "%~dp0..\frontend\video-pro-creator" >nul

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

echo Compilando Video Pro Creator...
call npm run build
if errorlevel 1 goto ERROR

echo Listo: frontend\video-pro-creator\dist
echo Abrí http://127.0.0.1:8000/video-pro/
popd >nul
exit /b 0

:ERROR
popd >nul
pause
exit /b 1
