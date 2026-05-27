@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo Cargando base turismo y exportando grilla 2026...
python -c "from backend.config.database import SessionLocal, init_db; from backend.services import turismo_service; init_db(); db=SessionLocal(); turismo_service.seed_database(db, force=True); p=turismo_service.exportar_grilla(db); print('OK', p); db.close()"
explorer "agents\data\turismo"
pause
