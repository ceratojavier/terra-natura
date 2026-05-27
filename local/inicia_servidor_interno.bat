@echo off

REM Ventana del servidor — si la cerrás, el programa queda apagado hasta que vuelvas a abrir el acceso directo.

setlocal EnableExtensions

chcp 65001 >nul

pushd "%~dp0.." >nul



where python >nul 2>&1 && (

  echo Iniciando Terra Natura...

  python -m backend.app

  popd >nul

  pause

  exit /b %ERRORLEVEL%

)



where py >nul 2>&1 && (

  echo Iniciando Terra Natura con py...

  py -3 -m backend.app

  popd >nul

  pause

  exit /b %ERRORLEVEL%

)



popd >nul

echo No se encuentra Python. Instalalo desde https://python.org y marca "Add to PATH".

pause


