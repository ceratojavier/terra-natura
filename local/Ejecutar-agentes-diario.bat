@echo off
chcp 65001 >nul
cd /d "%~dp0.."
python automation\run_daily_agents.py
pause
