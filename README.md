# YT Insight Backend

Backend API на Django для сервиса анализа YouTube-комментариев.

В этом репозитории находится именно backend: Django API, PostgreSQL, Redis и Celery worker.

## Что нужно для запуска

- Python `3.12`, если запускать локально
- Docker и Docker Compose, если запускать в контейнерах
- PostgreSQL
- Redis

## Быстрый запуск через Docker

Это основной и самый простой способ.

### 1. Подготовить `.env`

```bash
cp .env.example .env
```

Минимально проверь эти значения в `.env`:

```env
SECRET_KEY=change-me
DEBUG=True

DATABASE_NAME=yt_insight
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

REDIS_URL=redis://localhost:6379/0
FRONTEND_URL=http://localhost:3000
```

Примечание:

- Для `docker compose` значения `DATABASE_HOST` и `REDIS_URL` внутри контейнеров переопределяются автоматически.
- Ключи `YOUTUBE_API_KEY`, `DEEPSEEK_API_KEY`, `STRIPE_*`, `CLERK_*` нужны только для соответствующих интеграций. Без них проект поднимется, но связанные функции работать не будут.

### 2. Поднять сервисы

```bash
docker compose up --build
```

Запустятся:

- Django API
- PostgreSQL
- Redis
- Celery worker

`web` контейнер сам выполняет миграции при старте.

### 3. Открыть проект

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/api/schema/swagger/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`
- Admin: `http://localhost:8000/admin/`

### Полезные команды для Docker

```bash
# Запуск в фоне
docker compose up -d --build

# Логи
docker compose logs -f web
docker compose logs -f celery

# Создать суперпользователя
docker compose exec web python manage.py createsuperuser

# Остановить контейнеры
docker compose down

# Остановить и удалить volume с базой
docker compose down -v
```

Порты:

- Django API: `8000`
- PostgreSQL на хосте: `5433`
- Redis: `6379`

## Локальный запуск без Docker

Подходит, если PostgreSQL и Redis уже установлены локально.

### 1. Создать виртуальное окружение

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements/dev.txt
```

### 3. Подготовить `.env`

```bash
cp .env.example .env
```

Для локального запуска обычно достаточно таких значений:

```env
SECRET_KEY=change-me
DEBUG=True

DATABASE_NAME=yt_insight
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

REDIS_URL=redis://localhost:6379/0
FRONTEND_URL=http://localhost:3000
```

Если не используешь интеграции YouTube / DeepSeek / Stripe / Clerk прямо сейчас, их ключи можно временно оставить пустыми.

### 4. Подготовить базу данных

Нужно создать PostgreSQL-базу и убедиться, что `DATABASE_*` в `.env` совпадают с реальными доступами.

### 5. Применить миграции

```bash
python manage.py migrate
```

### 6. Создать администратора

```bash
python manage.py createsuperuser
```

### 7. Запустить Django

```bash
python manage.py runserver
```

### 8. В отдельном терминале запустить Celery

```bash
source .venv/bin/activate
celery -A config worker --loglevel=info --concurrency=4
```

После этого backend будет доступен на `http://localhost:8000`.

## Полезные команды

```bash
# Новые миграции
python manage.py makemigrations

# Проверка проекта
python manage.py check

# Тесты
python manage.py test

# Django shell
python manage.py shell
```

## Переменные окружения

### Обязательные для запуска

- `SECRET_KEY`
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `REDIS_URL`

### Нужны только для отдельных интеграций

- `YOUTUBE_API_KEY` - получение данных YouTube
- `DEEPSEEK_API_KEY` - AI-анализ комментариев
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_BASIC_PRICE_ID`
- `STRIPE_PRO_PRICE_ID`
- `CLERK_SECRET_KEY`
- `CLERK_JWKS_URL`
- `FRONTEND_URL`
- `RABBITMQ_URL`

## Структура запуска

- Django использует `config.settings.dev` по умолчанию
- HTTP API стартует через `python manage.py runserver`
- Фоновые задачи обрабатывает Celery
- Celery использует тот же `REDIS_URL`, что и backend

## Если что-то не стартует

Проверь по порядку:

1. Есть ли файл `.env`
2. Запущены ли PostgreSQL и Redis
3. Совпадают ли `DATABASE_*` с реальными доступами
4. Применились ли миграции
5. Установлены ли зависимости из `requirements/dev.txt`
