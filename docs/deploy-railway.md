# Деплой на Railway (полная инструкция)

Бот + Mini App в Telegram **24/7**, без ngrok и **без своего домена**.  
Railway выдаёт HTTPS-адреса вида `https://что-то.up.railway.app` — Telegram их принимает.

**Время:** ~40–60 минут при первом разе.  
**Стоимость:** trial ~$5 на 30 дней, дальше обычно **Hobby ~$5/мес** (API + бот + Postgres + Redis + miniapp).

---

## Что получится

| Компонент | Где живёт на Railway |
|-----------|----------------------|
| PostgreSQL | Плагин **Postgres** |
| Redis | Плагин **Redis** |
| FastAPI | Сервис **api** |
| aiogram-бот | Сервис **bot** |
| Mini App (React) | Сервис **miniapp** |

Два публичных URL:

- `https://…-api….up.railway.app` — backend
- `https://…-miniapp….up.railway.app` — Mini App (его открывает Telegram)

---

## Что нужно заранее

1. **Аккаунт [GitHub](https://github.com)** — код проекта в репозитории (публичный или private).
2. **Аккаунт [Railway](https://railway.com)** — регистрация через GitHub.
3. **Бот в Telegram** — [@BotFather](https://t.me/BotFather) → `/newbot` → скопировать **токен**.
4. **Ваш Telegram ID** — [@userinfobot](https://t.me/userinfobot) → число для админки.

Карта привязывается при регистрации Railway (trial). Своий домен **не нужен**.

---

## Часть 0. Код на GitHub

Если репозитория ещё нет:

```powershell
cd D:\work\projects\bg-club-bot
git init
git add .
git commit -m "Initial commit"
```

На GitHub: **New repository** → без README → скопировать URL.

```powershell
git remote add origin https://github.com/ВАШ_ЛОГИН/bg-club-bot.git
git branch -M main
git push -u origin main
```

Дальше Railway будет деплоить из этого репо.

---

## Часть 1. Проект Railway

1. Откройте [railway.com](https://railway.com) → **Login** → GitHub.
2. **New Project**.
3. **Deploy from GitHub repo** → выберите `bg-club-bot`.
4. Railway создаст первый сервис из репо — это пока черновик, его настроим.

---

## Часть 2. База данных и Redis

### PostgreSQL

1. В проекте: **+ New** → **Database** → **PostgreSQL**.
2. Сервис появится с именем вроде **Postgres** (запомните имя).

### Redis

1. **+ New** → **Database** → **Redis**.
2. Имя вроде **Redis**.

Оба сервиса должны быть в **Running**. Публичный домен им **не нужен**.

---

## Часть 3. Сервис API

Если Railway уже создал сервис из GitHub — переименуйте его в **api** (Settings → Service name).  
Иначе: **+ New** → **GitHub Repo** → тот же репозиторий → имя **api**.

### Настройки сборки

Откройте сервис **api** → **Settings**:

| Поле | Значение |
|------|----------|
| **Root Directory** | *(пусто)* |
| **Config file path** | `deploy/railway/api.railway.toml` |
| **Watch Paths** | уже в toml |

**Settings** → **Networking** → **Generate Domain** → скопируйте URL, например:

`https://bgclub-api-production-a1b2.up.railway.app`

Это **API_URL** — сохраните в блокнот.

### Переменные (api → Variables)

Нажмите **+ New Variable** → **Add Reference** для БД, остальное вручную.

| Переменная | Значение |
|------------|----------|
| `DATABASE_URL` | Reference → **Postgres** → `DATABASE_URL` |
| `REDIS_URL` | Reference → **Redis** → `REDIS_URL` |
| `SECRET_KEY` | случайная строка: `openssl rand -hex 32` или [random.org](https://www.random.org/strings/) |
| `ADMIN_TELEGRAM_IDS` | ваш Telegram ID |
| `DEV_AUTH_ENABLED` | `false` |
| `CORS_ORIGINS` | *пока оставьте пустым — заполните в Части 6* |
| `UPLOAD_DIR` | `/app/data/uploads` |
| `SESSION_REMINDER_HOURS` | `1` |
| `BGG_TOKEN` | опционально |

`DATABASE_URL` от Railway вида `postgresql://…` — проект сам добавит `+asyncpg`.

### Volume для картинок (рекомендуется)

**api** → **Settings** → **Volumes** → **Add Volume**:

- Mount path: `/app/data/uploads`

Без volume загруженные фото пропадут при пересборке.

### Деплой

**Deployments** → дождитесь **Success** (зелёный).

Проверка в браузере:

```
https://ВАШ-API.up.railway.app/api/v1/health
```

Ответ: `{"status":"ok"}`.

Если ошибка — **View Logs**, типичное: БД ещё не подключена (проверьте Reference Variables).

---

## Часть 4. Сервис Bot

1. **+ New** → **GitHub Repo** → тот же `bg-club-bot`.
2. Имя сервиса: **bot**.

### Настройки

| Поле | Значение |
|------|----------|
| **Config file path** | `deploy/railway/bot.railway.toml` |

**Networking** → домен **не генерируйте** (бот только исходящие запросы к Telegram).

### Переменные

| Переменная | Значение |
|------------|----------|
| `DATABASE_URL` | Reference → Postgres → `DATABASE_URL` |
| `REDIS_URL` | Reference → Redis → `REDIS_URL` |
| `TELEGRAM_BOT_TOKEN` | токен от BotFather |
| `TELEGRAM_BOT_USERNAME` | username бота без `@` |
| `SECRET_KEY` | **тот же**, что у api |
| `ADMIN_TELEGRAM_IDS` | ваш ID |
| `DEV_AUTH_ENABLED` | `false` |
| `MINIAPP_URL` | *заполните в Части 6* |

Деплой → в **Logs** должно быть `Bot started`.

---

## Часть 5. Сервис Mini App

1. **+ New** → **GitHub Repo** → `bg-club-bot`.
2. Имя: **miniapp**.

### Настройки

| Поле | Значение |
|------|----------|
| **Root Directory** | `miniapp` |
| **Config file path** | `deploy/railway/miniapp.railway.toml` |

### Переменная сборки (важно!)

**Variables** → **+ New Variable**:

| Переменная | Значение |
|------------|----------|
| `VITE_API_URL` | `https://ВАШ-API.up.railway.app` (из Части 3, **без** слэша в конце) |

Обязательно включите галочку **Available at Build Time** (или **Build Variable**).  
Без этого Mini App соберётся без URL API и в Telegram ничего не загрузится.

### Домен

**Networking** → **Generate Domain** → скопируйте, например:

`https://bgclub-miniapp-production-c3d4.up.railway.app`

Это **MINIAPP_URL** — сохраните.

Деплой → откройте MINIAPP_URL в браузере — должна открыться лента (данные пустые, если БД новая).

---

## Часть 6. Связать URL (второй проход)

Теперь известны оба адреса. Обновите переменные и **передеплойте** затронутые сервисы.

### miniapp (уже должен быть `VITE_API_URL`)

Проверьте, что `VITE_API_URL` = полный URL api. Если меняли — **Redeploy** miniapp.

### api

| Переменная | Значение |
|------------|----------|
| `CORS_ORIGINS` | `https://ВАШ-MINIAPP.up.railway.app` |

→ **Redeploy** api.

### bot

| Переменная | Значение |
|------------|----------|
| `MINIAPP_URL` | `https://ВАШ-MINIAPP.up.railway.app` |

→ **Redeploy** bot (кнопка меню «Открыть клуб» обновится).

---

## Часть 7. Проверка в Telegram

1. Найдите бота в Telegram → `/start`.
2. Кнопка меню слева от поля ввода → **Открыть клуб** (или как названо в i18n).
3. Mini App открывается внутри Telegram.
4. Ваш аккаунт (`ADMIN_TELEGRAM_IDS`) — админ-панель в профиле.

### Чеклист

- [ ] `/api/v1/health` → `ok`
- [ ] MINIAPP_URL открывается в браузере
- [ ] В Telegram Mini App грузит ленту / игры
- [ ] `/start` в боте работает
- [ ] `DEV_AUTH_ENABLED=false` на api и bot

---

## Первое наполнение клуба

В проде **нет** тестового seed. БД пустая.

1. Откройте Mini App в Telegram под админским аккаунтом.
2. **Профиль** → админ-раздел → настройки клуба, новости, игры.

Или локально один раз `seed_dev.py` — для прода проще через UI.

---

## Обновление после изменений в коде

```powershell
git add .
git commit -m "Описание изменений"
git push
```

Railway пересоберёт сервисы автоматически (если включён Auto Deploy).  
Иначе: каждый сервис → **Deployments** → **Redeploy**.

Если меняли только backend — достаточно api (+ bot при изменениях в `bot/`).  
Если меняли miniapp — redeploy **miniapp** (пересборка с `VITE_API_URL`).

---

## Схема переменных

```
Postgres ──DATABASE_URL──► api, bot
Redis    ──REDIS_URL─────► api, bot

API_URL  ──VITE_API_URL──► miniapp (build time)
MINIAPP_URL ──MINIAPP_URL──► bot
MINIAPP_URL ──CORS_ORIGINS──► api
```

---

## Стоимость (ориентир)

| План | Что даёт |
|------|----------|
| Trial | ~$5 кредитов, 30 дней |
| Free | ~$1/мес — **не хватит** на весь стек |
| Hobby | от $5/мес + usage — **норм для клуба** |

5 сервисов (Postgres, Redis, api, bot, miniapp) ≈ **$5–12/мес** на Hobby в зависимости от нагрузки.

---

## Частые проблемы

### Mini App белый экран / «Backend недоступен»

- `VITE_API_URL` задан и **Available at Build Time**?
- URL api без слэша в конце?
- После смены `VITE_API_URL` был **Redeploy miniapp** (не только api)?
- `curl https://API/api/v1/health` работает?

### CORS error в консоли (если смотрите через браузер)

- `CORS_ORIGINS` на api = точный URL miniapp (`https://…`, без `/` в конце).
- Redeploy api.

### Кнопка «Открыть клуб» не появляется

- `MINIAPP_URL` на bot = HTTPS URL miniapp.
- Redeploy bot.
- Подождите 1–2 минуты, перезайдите в чат с ботом.

### `Bot started`, но бот не отвечает

- Верный `TELEGRAM_BOT_TOKEN`?
- Только **один** инстанс бота на токен (не запущен локально `start_bot.bat`).

### Ошибки миграций в логах api

- Postgres в Running?
- `DATABASE_URL` — Reference на Postgres, не вручную с опечаткой?
- В логах: `alembic upgrade head` — если падает, скопируйте текст ошибки.

### Загрузки картинок пропадают

- Подключите **Volume** на api: `/app/data/uploads`.

### Сервис «засыпает» / биллинг

- На Free плане ресурсов мало — перейдите на **Hobby** (Settings → Billing).

---

## Railway vs VPS

| | Railway (эта инструкция) | [VPS + Caddy](deploy.md) |
|---|--------------------------|---------------------------|
| Домен | Не нужен | Желателен |
| HTTPS | Автоматически | Caddy + DNS |
| Сложность | Ниже | Выше |
| Цена | ~$5+/мес | VPS ~€4+/мес |

---

## Когда звать друга (крайний случай)

1. **Не получается привязать GitHub** к Railway (права организации).
2. **Платёж / регион** — карта не принимается.
3. После 2+ часов по чеклисту выше всё ещё не работает — попросите посмотреть **Logs** конкретного сервиса (скрин или текст ошибки).

Для отладки достаточно скриншотов: Variables сервисов api/bot/miniapp (без токена!) + последние 30 строк Logs.

---

## Справочник файлов в репозитории

| Файл | Назначение |
|------|------------|
| `deploy/railway/api.railway.toml` | Сборка и healthcheck API |
| `deploy/railway/bot.railway.toml` | Команда запуска бота |
| `deploy/railway/miniapp.railway.toml` | Сборка Mini App |
| `scripts/start_api_prod.sh` | Миграции + uvicorn на `$PORT` |
| `.env.railway.example` | Шпаргалка по переменным |
