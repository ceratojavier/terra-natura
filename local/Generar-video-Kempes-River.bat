@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Generando video RIVER - Kempes - Bialet Masse...
python -m ama.video.build_river_propias
explorer "ama\output\videos"
pause
