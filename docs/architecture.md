# Архитектура

## Обзор

```
Telegram Bot  ──┐
              ├──→  FastAPI  ──→  PostgreSQL
Mini App    ──┘         │
                        └──→  Redis (FSM, кэш, очереди)
```

## Основные сущности

```
users                 telegram_id, role, name
games                 каталог игр клуба
game_sessions         виртуальный стол (matchmaking)
session_participants  участники стола
announcements         новости
events                ивенты с датой/временем
table_bookings        заявки на физ. стол
memberships           абонементы
visits                check-in (membership | walk_in)
club_settings         часы, адрес, правила
```

### game_sessions

- `game_id` — nullable (из каталога)
- `custom_game_title` — nullable («своя игра»)
- `starts_at`, `max_players`, `status` (open | full | cancelled | completed)
- `note`, `creator_id`

При join: если `participants.count == max_players` → `full` → push всем участникам и админу.

### events vs announcements

Разные таблицы. В UI — общая «лента» на главной + отдельные экраны «Календарь» и «Новости».

## API (черновик)

```
# Публичное
GET  /club
GET  /games
GET  /announcements
GET  /events
GET  /feed                    # ближайшие ивенты + новости

# Виртуальные столы
GET    /sessions?status=open
POST   /sessions
POST   /sessions/{id}/join
DELETE /sessions/{id}/leave
PATCH  /sessions/{id}/cancel

# Бронь физ. стола
GET  /bookings/me
POST /bookings

# Профиль
GET  /me
GET  /me/visits
GET  /me/membership

# Admin
CRUD /admin/games, /admin/events, /admin/announcements
POST /admin/memberships
POST /admin/visits
DELETE /admin/sessions/{id}
PATCH  /admin/bookings/{id}
```

Авторизация Mini App: проверка `Telegram.WebApp.initData` на backend.

## Структура репозитория

```
bg-club-bot/
├── api/           # FastAPI
├── bot/           # aiogram
├── miniapp/       # frontend Mini App
├── docs/
├── docker-compose.yml
└── README.md
```
