@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
set "ROOT=%CD%"

echo ========================================
echo  BG Club — запуск всего окружения
echo ========================================
echo.

if not exist ".env" (
    echo [ERROR] Нет файла .env — скопируйте .env.example в .env
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker не запущен. Сначала откройте Docker Desktop и дождитесь Engine running.
    exit /b 1
)

echo [1/5] PostgreSQL и Redis...
docker compose up postgres redis -d
if errorlevel 1 (
    echo [ERROR] Не удалось поднять postgres/redis
    exit /b 1
)

echo       Ждём PostgreSQL...
set /a DB_TRIES=0
:wait_postgres
set /a DB_TRIES+=1
if %DB_TRIES% gtr 30 (
    echo [ERROR] PostgreSQL не ответил за 60 секунд
    exit /b 1
)
docker compose exec -T postgres pg_isready -U bgclub -d bgclub >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_postgres
)
echo       OK
echo.

echo [2/5] API...
start "BG Club API" cmd /k pushd "%ROOT%" ^&^& call scripts\start_api.bat

echo       Ждём API (pip, миграции, uvicorn)...
set /a API_TRIES=0
:wait_api
set /a API_TRIES+=1
if %API_TRIES% gtr 90 (
    echo [WARN] API не ответил за 3 минуты — смотрите окно "BG Club API"
    goto start_miniapp
)
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/health' -UseBasicParsing -TimeoutSec 2).StatusCode | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_api
)
echo       OK
echo.

:start_miniapp
echo [3/5] Mini App...
start "BG Club Mini App" cmd /k pushd "%ROOT%\miniapp" ^&^& npm run dev
timeout /t 2 /nobreak >nul

echo [4/5] ngrok...
if not exist "tools\ngrok\ngrok.exe" (
    echo [WARN] ngrok не найден — пропускаем. См. tools\ngrok\ или docs\telegram-testing.md
) else (
    start "BG Club ngrok" cmd /k pushd "%ROOT%" ^&^& call scripts\start_ngrok.bat
    timeout /t 2 /nobreak >nul
)

echo [5/5] Telegram-бот...
start "BG Club Bot" cmd /k pushd "%ROOT%" ^&^& call scripts\start_bot.bat

echo.
echo ========================================
echo  Готово. Открыто 4 окна:
echo    - BG Club API
echo    - BG Club Mini App
echo    - BG Club ngrok  ^(если установлен^)
echo    - BG Club Bot
echo.
echo  Mini App:  http://localhost:5173
echo  API docs:  http://localhost:8000/docs
echo.
echo  Не закрывайте эти окна, пока работаете.
echo  Красные proxy error в Mini App — API ещё не поднялся; обновите страницу.
echo  Если ngrok дал новый URL — обновите MINIAPP_URL в .env
echo  и перезапустите окна API и Bot.
echo ========================================
echo.

endlocal
