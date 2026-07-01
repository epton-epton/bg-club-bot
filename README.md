# bg-club-bot

Telegram-бот и Mini App для клуба настольных игр.

## Документация

- [Требования](docs/requirements.md)
- [Архитектура](docs/architecture.md)
- [Локальный запуск](docs/local-dev.md) — что делать после перезагрузки ПК
- [Тест в Telegram](docs/telegram-testing.md) — ngrok, бот, телефон, чеклист MVP 2
- [Деплой в прод](docs/deploy.md) — VPS, Docker, HTTPS, без ngrok
- [Деплой на Railway](docs/deploy-railway.md) — без домена и VPS, пошагово
- [Backlog](docs/backlog.md) — отложенные фичи
- [Дизайн](docs/design.md) — бренд и UI

## Стек

Python · aiogram 3 · FastAPI · PostgreSQL · Redis · Mini App (React)

## Быстрый старт (Docker)

```bash
cp .env.example .env
# Заполнить TELEGRAM_BOT_TOKEN (обязательно для бота)
# MINIAPP_URL=http://localhost:5173 — для кнопки меню в боте (локально)

docker compose up --build
```

После запуска:

| Сервис | URL |
|--------|-----|
| Mini App | http://localhost:5173 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/api/v1/health |
| Клуб | http://localhost:8000/api/v1/club |
| Игры | http://localhost:8000/api/v1/games |
| Лента | http://localhost:8000/api/v1/feed |

При первом `docker compose up` автоматически выполняются миграции и `scripts/seed_dev.py` (тестовые данные).

Mini App: три вкладки — **Лента**, **Игры**, **О клубе**.

Для Telegram нужен HTTPS ([Railway](docs/deploy-railway.md) / [VPS](docs/deploy.md) / ngrok). Локально Mini App открывается в браузере.

## Mini App (отдельно)

```bash
cd miniapp
npm install
npm run dev
```

API должен быть на `localhost:8000` — Vite проксирует `/api` автоматически.

Если `npm install` падает с `UNABLE_TO_VERIFY_LEAF_SIGNATURE` — обычно виноват корпоративный прокси/антивирус. Нужно добавить корневой сертификат в доверенные или настроить `NODE_EXTRA_CA_CERTS`.

## Telegram (реальное тестирование)

Пошагово: **[docs/telegram-testing.md](docs/telegram-testing.md)** — BotFather, ngrok, 4 терминала, чеклист столов и уведомлений.

## Локальная разработка (без Docker)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt

# PostgreSQL и Redis должны быть запущены (или только postgres/redis из compose)
docker compose up postgres redis -d

cp .env.example .env
# Настроить .env

set PYTHONPATH=shared;api;bot   # PowerShell: $env:PYTHONPATH="shared;api;bot"
alembic upgrade head
python scripts/seed_dev.py
uvicorn bgclub_api.main:app --reload
# В другом терминале:
cd miniapp && npm install && npm run dev
# В третьем терминале (опционально):
python -m bgclub_bot.main
```

## Структура

```
bg-club-bot/
├── api/           # FastAPI
├── bot/           # aiogram
├── shared/        # конфиг, модели БД, сервисы
├── alembic/       # миграции
├── miniapp/       # React Mini App
├── docs/
└── docker-compose.yml
```
