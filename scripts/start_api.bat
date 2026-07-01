@echo off
setlocal
cd /d "%~dp0.."
set PYTHONPATH=shared;api;bot

if not exist ".env" (
    echo Нет файла .env — скопируйте .env.example в .env
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Создаю venv...
    python -m venv .venv
)

echo Зависимости Python...
.venv\Scripts\pip install -r requirements.txt -q
if errorlevel 1 exit /b 1

echo Миграции...
.venv\Scripts\alembic upgrade head
if errorlevel 1 exit /b 1

echo Тестовые данные...
.venv\Scripts\python scripts\seed_dev.py
if errorlevel 1 (
    echo WARNING: seed не удался, API запустится без тестовых данных.
)

echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
.venv\Scripts\uvicorn bgclub_api.main:app --reload --host 0.0.0.0 --port 8000
