@echo off
cd /d "%~dp0.."
echo Sincronizando Córdoba Turismo (API / sync local / Playwright)...
py -m ama.scrapers.sources_cordoba_turismo %*
echo.
echo Si dio 403, segui docs\SYNC_CORDOBA_TURISMO.md y volve a correr Actualizar-agenda-eventos.bat
pause
