@echo off
cd /d "%~dp0.."
echo Actualizando agenda de eventos Terra Natura...
py -m backend.jobs.actualizar_agenda_semanal
pause
