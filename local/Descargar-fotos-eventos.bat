@echo off
cd /d "%~dp0.."
echo Terra Natura — Descargando fotos de eventos desde la web...
echo (Necesita internet. La primera vez Cursor puede pedir permiso: Allow for workspace)
py -c "from datetime import date; from ama.scrapers.event_image_fetcher import descargar_desde_confirmados_y_cache; r=descargar_desde_confirmados_y_cache(desde=date.today()); print(r.get('mensaje',r))"
pause
