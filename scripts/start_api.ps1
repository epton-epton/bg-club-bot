# Запуск API для локальной разработки Mini App
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$env:PYTHONPATH = "shared;api;bot"

if (-not (Test-Path ".env")) {
    Write-Host "Нет файла .env — скопируйте: cp .env.example .env" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Создаю venv и ставлю зависимости Python..."
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

Write-Host "Миграции..."
.\.venv\Scripts\alembic upgrade head

Write-Host "Тестовые данные (если БД пустая)..."
.\.venv\Scripts\python scripts\seed_dev.py

Write-Host "API: http://localhost:8000" -ForegroundColor Green
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Green
.\.venv\Scripts\uvicorn bgclub_api.main:app --reload --host 0.0.0.0 --port 8000
