@echo off

setlocal EnableExtensions

cd /d "%~dp0.."

set NGROK=%~dp0..\tools\ngrok\ngrok.exe

if not exist "%NGROK%" (
    echo ngrok не найден: tools\ngrok\ngrok.exe
    echo Скачайте с https://ngrok.com/download или попросите ассистента установить.
    exit /b 1
)

if not exist ".env" (
    echo [ERROR] Нет файла .env
    exit /b 1
)

set "MINIAPP_URL="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "$line = Get-Content -LiteralPath '.env' | Where-Object { $_ -match '^MINIAPP_URL=' } | Select-Object -First 1; if ($line) { ($line -split '=', 2)[1].Trim() }"`) do set "MINIAPP_URL=%%i"

echo Туннель на Mini App :5173
echo.

echo %MINIAPP_URL% | findstr /i "ngrok" >nul 2>&1
if errorlevel 1 (
    echo MINIAPP_URL не ngrok — будет случайный URL при каждом запуске.
    echo Скопируйте HTTPS из Forwarding в MINIAPP_URL и CORS_ORIGINS (.env^), перезапустите бота.
    echo.
    "%NGROK%" http 5173
) else (
    set "NGROK_DOMAIN="
    for /f "usebackq delims=" %%d in (`powershell -NoProfile -Command "([uri]'%MINIAPP_URL%').Host"`) do set "NGROK_DOMAIN=%%d"
    echo Статический домен: %NGROK_DOMAIN%
    echo Должен совпадать с MINIAPP_URL в .env
    echo.
    "%NGROK%" http --domain=%NGROK_DOMAIN% 5173
)

endlocal
