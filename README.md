# AntiFraud System (Tier 0)

Backend-сервис для антифрод-проверок на **FastAPI + PostgreSQL + Redis**.

На текущем этапе реализован **Tier 0**:
- полноценные CRUD-операции для пользователей и антифрод-правил;
- аутентификация и авторизация по JWT;
- создание и получение транзакций;
- batch-обработка транзакций;
- DSL-валидация выражений правил;
- при принятии решения по транзакциям правила пока **не исполняются** (`matched=false`), но структура ответа и пайплайн уже готовы.

## Стек

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Docker / Docker Compose

## Структура проекта

```text
app/
  api/            # HTTP роуты
  core/           # конфиг, БД, зависимости, безопасность, обработка ошибок
  dsl/            # токенайзер/AST/парсер/валидация DSL
  models/         # SQLAlchemy-модели
  schemas/        # Pydantic-схемы запросов/ответов
  services/       # бизнес-логика
  main.py         # точка входа FastAPI
```

## Быстрый старт (Docker Compose)

### 1) Запуск

```bash
docker compose up --build
```

После старта API доступно на `http://localhost:8000`.

### 2) Проверка

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Ping: `GET http://localhost:8000/api/v1/ping`
- Встроенный UI для ручного тестирования: `http://localhost:8000/ui`

### 3) Администратор по умолчанию

При первом старте автоматически создаётся пользователь с ролью `ADMIN`
(берётся из переменных окружения):

- `ADMIN_EMAIL=admin@example.com`
- `ADMIN_PASSWORD=Admin1234`
- `ADMIN_FULLNAME=Admin`

## Запуск локально (без Docker)

### 1) Установите зависимости

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Поднимите PostgreSQL и Redis

Нужно обеспечить доступные инстансы PostgreSQL и Redis (локально или удалённо).

### 3) Установите переменные окружения

Пример:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=antifraud
export DB_USER=antifraud
export DB_PASSWORD=antifraud

export REDIS_HOST=localhost
export REDIS_PORT=6379

export RANDOM_SECRET=super-secret
export ADMIN_EMAIL=admin@example.com
export ADMIN_FULLNAME=Admin
export ADMIN_PASSWORD=Admin1234
```

### 4) Запустите приложение

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Ключевые API-эндпоинты

### Health
- `GET /api/v1/ping`

### Auth
- `POST /api/v1/auth/register` — регистрация USER
- `POST /api/v1/auth/login` — логин и JWT

### Users
- `GET /api/v1/users/me`
- `PUT /api/v1/users/me`
- `GET /api/v1/users/{id}`
- `PUT /api/v1/users/{id}`
- `GET /api/v1/users` (ADMIN)
- `POST /api/v1/users` (ADMIN)
- `DELETE /api/v1/users/{id}` (ADMIN, деактивация)

### Fraud Rules
- `POST /api/v1/fraud-rules` (ADMIN)
- `GET /api/v1/fraud-rules` (ADMIN)
- `GET /api/v1/fraud-rules/{id}` (ADMIN)
- `PUT /api/v1/fraud-rules/{id}` (ADMIN)
- `DELETE /api/v1/fraud-rules/{id}` (ADMIN, soft delete через `enabled=false`)
- `POST /api/v1/fraud-rules/validate` — проверка DSL-выражения

### Transactions
- `POST /api/v1/transactions`
- `GET /api/v1/transactions/{id}`
- `GET /api/v1/transactions`
- `POST /api/v1/transactions/batch`

## Особенности Tier 0

1. Движок правил в решении по транзакциям пока не включен:
   - `matched=false` для всех правил,
   - итоговый статус транзакции в Tier 0 — `APPROVED`.
2. Список `ruleResults` возвращается в ответе для совместимости со следующими tier.
3. Для `ADMIN` при создании транзакции обязателен `userId`, для `USER` `userId` из body игнорируется.
4. В batch-режиме каждый элемент обрабатывается независимо; при частичных ошибках возвращается `207`.

## Пример запросов

### Логин

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"Admin1234"}'
```

### Создание правила (ADMIN)

```bash
curl -X POST http://localhost:8000/api/v1/fraud-rules \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Big amounts",
    "description": "Tier0 rule",
    "dslExpression": "amount > 10000",
    "enabled": true,
    "priority": 10
  }'
```

### Создание транзакции (ADMIN)

```bash
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{
    "userId": "<USER_ID>",
    "amount": 15000,
    "currency": "RUB",
    "timestamp": "2026-01-01T12:00:00Z"
  }'
```

## Переменные окружения

Обязательные для корректного старта:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `ADMIN_EMAIL`
- `ADMIN_FULLNAME`
- `ADMIN_PASSWORD`

Опциональные:

- `REDIS_HOST` (по умолчанию `localhost`)
- `REDIS_PORT` (по умолчанию `6379`)
- `RANDOM_SECRET` (по умолчанию `dev-secret`, для production обязательно переопределить)

## Примечания

- Таблицы создаются автоматически при старте приложения.
- Миграции через Alembic в репозитории пока не настроены как основной путь развёртывания.
- Redis подключён и готов к использованию в следующих этапах развития (rate-limit, кэш, очереди и т.д.).
