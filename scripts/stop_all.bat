@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

echo Останавливаю контейнеры postgres и redis...
docker compose stop postgres redis

echo.
echo Окна API / Mini App / ngrok / Bot закройте вручную ^(Ctrl+C или крестик^).
echo.

endlocal
