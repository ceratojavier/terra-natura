@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Analiza reels guardados en marketing\sistema\referencias_reels\videos\
echo Guarda ahi MP4 de Instagram que te gusten (solo estudio).
echo.
python -m ama.engine.reel_reference_probe
echo.
echo Ficha actualizada: marketing\sistema\referencias_reels\indice.json
pause
