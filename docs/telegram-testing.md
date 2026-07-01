# Тестирование в реальном Telegram

Пошаговая настройка: бот + Mini App на телефоне + уведомления (MVP 2).

## Что получится в итоге

- `/start` в боте — регистрация и приветствие
- Кнопка **«Открыть клуб»** — Mini App внутри Telegram
- Вкладка **Столы** — создание, join, обложки игр
- Push в чат: присоединился, стол полный, отмена, напоминание

---

## Что нужно один раз

| Что | Зачем |
|-----|--------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | PostgreSQL + Redis |
| Python venv (создаёт `start_api.bat`) | API и бот |
| Node.js 20+ | Mini App |
| ngrok (в проекте: `tools\ngrok\` или [скачать](https://ngrok.com/download)) | HTTPS-туннель для Telegram |
| Бот в [@BotFather](https://t.me/BotFather) | `TELEGRAM_BOT_TOKEN` |
| Второй Telegram-аккаунт (друг, второй телефон) | Проверка join и уведомлений |

---

## Шаг 1. Создать бота

1. Открыть [@BotFather](https://t.me/BotFather) → `/newbot`
2. Имя и username бота (должен заканчиваться на `bot`)
3. Скопировать **токен** → в `.env`:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...
```

4. Узнать свой Telegram ID — написать [@userinfobot](https://t.me/userinfobot) или [@getmyid_bot](https://t.me/getmyid_bot):

```env
ADMIN_TELEGRAM_IDS=ваш_id_числом
```

После этого при `/start` у вас будет роль **админ** (кнопка «Удалить» на столах).

---

## Шаг 2. Поднять backend и Mini App

Как в [local-dev.md](local-dev.md):

```powershell
# Docker Desktop → Engine running

cd D:\work\projects\bg-club-bot
docker compose up postgres redis -d
```

**Терминал 1 — API** (не закрывать):

```powershell
cd D:\work\projects\bg-club-bot
scripts\start_api.bat
```

Проверка: http://localhost:8000/api/v1/feed — JSON.

**Терминал 2 — Mini App** (не закрывать):

```powershell
cd D:\work\projects\bg-club-bot\miniapp
npm run dev
```

Проверка в браузере: http://localhost:5173 — лента, игры.

---

## Шаг 3. ngrok — HTTPS для Telegram

### Один раз: токен ngrok

В [dashboard.ngrok.com](https://dashboard.ngrok.com) скопировать authtoken, затем:

```powershell
D:\work\projects\bg-club-bot\tools\ngrok\ngrok.exe config add-authtoken ВАШ_ТОКЕН
```

### Запуск туннеля

Telegram **не открывает** `http://localhost` на телефоне. Нужен публичный HTTPS.

**Терминал 3 — ngrok** (не закрывать):

```powershell
cd D:\work\projects\bg-club-bot
scripts\start_ngrok.bat
```

> ngrok лежит в `tools\ngrok\` (не в git). Первый раз — настроить токен (см. ниже).

В выводе скопировать **Forwarding** HTTPS-URL, например:

```
https://a1b2c3d4.ngrok-free.app
```

> Если в `.env` уже есть **закреплённый** домен ngrok (`*.ngrok-free.dev` / `*.ngrok-free.app`), `scripts\start_ngrok.bat` поднимет туннель с `--domain=...` автоматически — URL в боте менять не нужно.
>
> Без закреплённого домена бесплатный ngrok при каждом запуске даёт **новый URL** — после перезапуска ngrok нужно обновить `.env` и перезапустить бота (шаг 4).

---

## Шаг 4. Настроить `.env` для Telegram

Открыть `D:\work\projects\bg-club-bot\.env`:

```env
TELEGRAM_BOT_TOKEN=...ваш токен...
MINIAPP_URL=https://a1b2c3d4.ngrok-free.app
CORS_ORIGINS=http://localhost:5173,https://a1b2c3d4.ngrok-free.app
ADMIN_TELEGRAM_IDS=ваш_telegram_id

# Для теста в Telegram лучше выключить — будет настоящий initData
DEV_AUTH_ENABLED=false
```

Сохранить файл.

**Перезапустить API** (терминал 1): `Ctrl+C` → снова `scripts\start_api.bat`.

---

## Шаг 5. Запустить бота

**Терминал 4 — бот** (не закрывать):

```powershell
cd D:\work\projects\bg-club-bot
scripts\start_bot.bat
```

В логе должно быть `Bot started`. Бот при старте выставляет кнопку меню **«Открыть клуб»** на URL из `MINIAPP_URL`.

---

## Шаг 6. Открыть на телефоне

1. Telegram на телефоне → найти своего бота
2. `/start` — приветствие в чате
3. Слева от поля ввода — **«Открыть клуб»** (иконка меню)
4. Mini App откроется внутри Telegram

Если видите страницу ngrok «Visit Site» — нажать **Visit Site** (особенность бесплатного ngrok).

### Если Mini App не открывается

- Проверить, что работают **все 4 процесса**: API, miniapp, ngrok, bot
- `MINIAPP_URL` в `.env` = **тот же** HTTPS-URL, что в ngrok (без `/` в конце)
- Перезапустить бота после смены `.env`
- Открыть ngrok-URL в обычном браузере — должна открыться Mini App

### Если «Unauthorized» на вкладке Столы

- В Telegram `initData` приходит автоматически — `DEV_AUTH_ENABLED` должен быть `false`
- Перезапустить API после смены `.env`

---

## Шаг 7. Чеклист теста MVP 2 (~20 минут)

### A. Один аккаунт (вы)

| # | Действие | Ожидание |
|---|----------|----------|
| 1 | `/start` | Приветствие в чате |
| 2 | «Открыть клуб» | Mini App, 4 вкладки |
| 3 | Игры | Каталог с обложками (миниатюры) |
| 4 | Столы → Создать | Стол из **каталога**, время через 2+ ч |
| 5 | Карточка стола | Обложка игры фоном |

### B. Два аккаунта (вы + друг)

| # | Действие | Ожидание |
|---|----------|----------|
| 6 | Друг: `/start` у того же бота | Регистрация |
| 7 | Друг: Столы → Присоединиться | Успех |
| 8 | Вы | Push: «присоединился к столу» |
| 9 | Другие join до полного стола | Push всем: «встреча состоится» |
| 10 | Вы (админ) | Push о полном столе |
| 11 | Создатель: Отменить стол | Push участникам об отмене |

### C. Напоминание (опционально, ~1 ч ожидания)

1. Создать стол с началом **через 61 минуту**
2. Бот должен работать всё время (`SESSION_REMINDER_HOURS=1` в `.env`)
3. За ~1 ч до начала — push «Напоминание» всем участникам

---

## Шпаргалка: что должно быть запущено

| Терминал | Команда | Порт |
|----------|---------|------|
| — | Docker Desktop | — |
| 1 | `scripts\start_api.bat` | 8000 |
| 2 | `npm run dev` в `miniapp/` | 5173 |
| 3 | `ngrok http 5173` | публичный HTTPS |
| 4 | `scripts\start_bot.bat` | — |

---

## Частые проблемы

### ERR_NGROK_3200 на телефоне (в Cursor работает)

Туннель **offline**: ngrok не запущен, упал, или URL в боте не совпадает с тем, что реально слушает ngrok.

1. Окно **BG Club ngrok** открыто? В `Forwarding` должно быть:
   `https://sandy-kitchen-evolve.ngrok-free.dev` — **тот же** хост, что в `MINIAPP_URL` в `.env`.
2. Если в ngrok другой URL — либо обновите `.env` + перезапустите бота, либо перезапустите ngrok через `scripts\start_ngrok.bat` (скрипт читает домен из `MINIAPP_URL`).
3. Mini App на `:5173` должна работать (окно **BG Club Mini App**).
4. Проверка с ПК: откройте `MINIAPP_URL` в браузере — должна открыться Mini App, не страница ngrok с 3200.

### ngrok URL сменился

1. Скопировать новый HTTPS из ngrok
2. Обновить `MINIAPP_URL` и `CORS_ORIGINS` в `.env`
3. Перезапустить API и бота

### Бот не шлёт уведомления

- Бот запущен? (терминал 4)
- `TELEGRAM_BOT_TOKEN` настоящий, не заглушка?
- Пользователь писал боту `/start` (иначе Telegram не доставит сообщения)

### Обложка стола не видна

- Стол создан **из каталога**, не «своя игра»
- В каталоге есть игры с BGG (см. вкладка Игры)

### Тест в браузере на localhost сломался после `DEV_AUTH_ENABLED=false`

Для браузера без Telegram снова включите:

```env
DEV_AUTH_ENABLED=true
```

Для теста в Telegram — `false`. Можно переключать по ситуации.

---

## Дальше: деплой вместо ngrok

Когда устанете обновлять ngrok-URL:

- VPS + Docker
- Домен + HTTPS (Let's Encrypt)
- `MINIAPP_URL=https://club.yourdomain.com`
- Бот и API на сервере 24/7

До MVP 5 ngrok достаточно для полноценных тестов.
