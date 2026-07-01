# Локальный запуск (после перезагрузки ПК)

Краткая инструкция: как поднять Mini App и API на своей машине.

## Что нужно установить один раз

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (WSL2 обновлён)
- Python 3.12+ (для API)
- Node.js 20+ (для Mini App)

Файл `.env` в корне проекта (скопировать из `.env.example`).

---

## Каждый раз после перезагрузки

### 1. Docker Desktop

Запустить приложение и дождаться статуса **Engine running** внизу окна.

Регистрация в Docker Hub **не обязательна** — можно Skip.

### 2. Терминал 1 — PostgreSQL и Redis

```powershell
cd D:\work\projects\bg-club-bot
docker compose up postgres redis -d
```

Проверка:

```powershell
docker compose ps
```

У `postgres` и `redis` должно быть **running**.

Это окно можно закрыть.

### 3. Терминал 2 — API

```powershell
cd D:\work\projects\bg-club-bot
scripts\start_api.bat
```

Окно **не закрывать** — API должен работать всё время.

Проверка в браузере: http://localhost:8000/api/v1/feed — JSON с событиями и новостями.

> Если PowerShell ругается на `.ps1` — используйте `start_api.bat`, не `start_api.ps1`.

### 4. Терминал 3 — Mini App

```powershell
cd D:\work\projects\bg-club-bot\miniapp
npm run dev
```

Окно **не закрывать**.

Открыть в браузере: http://localhost:5173

В браузере нет Telegram `initData`, поэтому для вкладки **Столы** и `/me` в `.env` должно быть:

```env
DEV_AUTH_ENABLED=true
DEV_TELEGRAM_ID=999999001
```

Mini App в режиме `npm run dev` автоматически шлёт заголовок `Authorization: dev`. После смены `.env` перезапустите API (`Ctrl+C` → `scripts\start_api.bat`).

---

## Шпаргалка

| Шаг | Действие | Закрывать окно? |
|-----|----------|-----------------|
| 1 | Docker Desktop → Engine running | — |
| 2 | `docker compose up postgres redis -d` | да |
| 3 | `scripts\start_api.bat` | **нет** |
| 4 | `npm run dev` в `miniapp/` | **нет** |

---

## Что где открывается

| URL | Что это |
|-----|---------|
| http://localhost:5173 | Mini App (то, что будет в Telegram) |
| http://localhost:8000/docs | Swagger API |
| http://localhost:8000/api/v1/feed | Лента (проверка данных) |

---

## Тест в реальном Telegram

Для Mini App в браузере бот **не нужен**.

Полная инструкция (ngrok, телефон, уведомления, чеклист MVP 2):

**[docs/telegram-testing.md](telegram-testing.md)**

Прод без ngrok: **[docs/deploy-railway.md](deploy-railway.md)** (Railway, без домена) или **[docs/deploy.md](deploy.md)** (VPS).

Кратко: Docker + API + `npm run dev` + `ngrok http 5173` + `scripts\start_bot.bat`, в `.env` — токен бота и HTTPS-URL из ngrok в `MINIAPP_URL`.

---

## Частые проблемы

### `ECONNREFUSED` / ошибка API в Mini App

API не запущен. Запустите терминал 2 (`start_api.bat`).

### `club_settings does not exist` / ошибки миграций

Пересоздать БД и миграции:

```powershell
cd D:\work\projects\bg-club-bot
docker compose down -v
docker compose up postgres redis -d
```

Подождать ~10 секунд, затем снова `scripts\start_api.bat`.

### `connection is closed` в терминале API

PostgreSQL перезапускался, а API остался со старым подключением. В терминале API: **Ctrl+C**, затем снова `scripts\start_api.bat`.

### `npm install` — `UNABLE_TO_VERIFY_LEAF_SIGNATURE`

Проблема SSL (прокси/антивирус). Попробовать другую сеть или настроить `NODE_EXTRA_CA_CERTS` (см. README).

### Скрипты `.ps1` не запускаются

Используйте `scripts\start_api.bat` вместо `.ps1`.

---

## Первый запуск с нуля

```powershell
cd D:\work\projects\bg-club-bot
cp .env.example .env
# заполнить .env при необходимости

docker compose up postgres redis -d
scripts\start_api.bat

# в другом терминале:
cd miniapp
npm install
npm run dev
```
