@echo off

setlocal

cd /d "%~dp0.."

set PYTHONPATH=shared;api;bot



if not exist ".env" (

    echo Нет файла .env — скопируйте .env.example в .env

    exit /b 1

)



if not exist ".venv\Scripts\python.exe" (

    echo Нет .venv — сначала запустите scripts\start_api.bat

    exit /b 1

)



echo Bot polling... Нужен TELEGRAM_BOT_TOKEN в .env

echo Mini App URL: см. MINIAPP_URL в .env

echo Инструкция: docs\telegram-testing.md

.venv\Scripts\python -m bgclub_bot.main

