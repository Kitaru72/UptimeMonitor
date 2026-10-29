# UptimeMonitor

UptimeMonitor — API для проверки доступности сайтов. Он хранит адреса наблюдаемых сайтов, выполняет HTTP-проверки и сохраняет историю ответов в PostgreSQL.

Проверки запускаются вручную: для одного сайта через `POST /monitors/{monitor_id}/checks` или для всех активных сайтов через `POST /checks/run`. Автоматического расписания пока нет.

## Возможности

- Создание, просмотр, удаление, приостановка и возобновление мониторов.
- Проверка URL с фиксацией статуса `UP`/`DOWN`, HTTP-кода, типа сетевой ошибки и времени ответа.
- Параллельная проверка активных мониторов с сохранением результатов в базу данных.
- Постраничный просмотр мониторов и истории проверок через `limit` и `offset`.
- Проверка доступности базы данных через `GET /ready`.

## Стек

Python 3.13, FastAPI, HTTPX, SQLAlchemy (async), PostgreSQL 16, Alembic, uv, Docker Compose и pytest.

## Быстрый запуск через Docker Compose

Нужны Docker и Docker Compose. Из корня проекта:

```powershell
Copy-Item .env.example .env
```

На Linux или macOS вместо этого используйте `cp .env.example .env`. Откройте `.env` и задайте свой пароль в `DB_PASSWORD`. Переменные `DB_NAME` и `DB_USER` задают имя базы и пользователя PostgreSQL. Для сервисов Compose адрес базы уже установлен как `DB_HOST=db` и порт `DB_PORT=5432` в `compose.yaml`; значение `DB_HOST` из `.env` для этих сервисов переопределяется.

```text
DB_NAME=uptime_monitor
DB_USER=uptime_monitor_user
DB_PASSWORD=replace_with_your_password
```

Файл `.env` содержит секреты и не должен попадать в Git. Если API должен быть доступен только с самого хоста, добавьте в `.env` строку `API_BIND_HOST=127.0.0.1`. Без неё порт 8000 публикуется на всех сетевых интерфейсах хоста.

Запустите сервисы:

```text
docker compose up -d --build
docker compose ps -a
```

Compose поднимет PostgreSQL, дождётся его состояния `healthy`, применит миграции Alembic в одноразовом сервисе `migrate` и запустит API. В `docker compose ps -a` ожидаются `db` со статусом `healthy`, `migrate` со статусом `Exited (0)` и работающий `api`.

После запуска откройте [Swagger UI](http://localhost:8000/docs) или проверьте готовность API:

```text
curl http://localhost:8000/ready
```

При доступной базе `/ready` возвращает HTTP 200 и `{"status":"ready"}`. При недоступной базе — HTTP 503 и `{"status":"unavailable"}`. В PowerShell можно использовать `curl.exe -i http://localhost:8000/ready`, чтобы увидеть HTTP-код.

Посмотреть логи и остановить приложение:

```text
docker compose logs --tail 50 api
docker compose down
```

`docker compose down` удаляет контейнеры и сеть, но сохраняет данные PostgreSQL в именованном томе `pg_data`.

## Основные маршруты

| Метод | Маршрут | Назначение |
| --- | --- | --- |
| `GET` | `/monitors` | Список мониторов |
| `POST` | `/monitors` | Создать монитор |
| `GET` | `/monitors/{monitor_id}` | Получить монитор |
| `DELETE` | `/monitors/{monitor_id}` | Удалить монитор |
| `POST` | `/monitors/{monitor_id}/pause` | Приостановить монитор |
| `POST` | `/monitors/{monitor_id}/resume` | Возобновить монитор |
| `GET` | `/monitors/{monitor_id}/checks` | История проверок монитора |
| `POST` | `/monitors/{monitor_id}/checks` | Проверить один сайт |
| `POST` | `/checks/run` | Проверить все активные сайты |
| `GET` | `/ready` | Проверить соединение с базой |

Для списков доступны параметры `limit` (по умолчанию 20, от 1 до 100) и `offset` (по умолчанию 0, от 0). Ответ содержит `items`, `total`, `limit` и `offset`. История проверок отсортирована от новых к старым.

Пример создания монитора в PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/monitors -ContentType 'application/json' -Body '{"url":"https://example.com"}'
```

Затем можно запустить проверку через Swagger UI или вызвать `POST /checks/run`. Сайт считается доступным при HTTP-коде от 200 до 399; таймауты и ошибки соединения записываются как `DOWN`.

## Локальная разработка

Для запуска Python вне контейнера потребуются Python 3.13, uv и доступная PostgreSQL. В `.env` укажите адрес и порт этой базы: в отличие от Compose, локальный Python использует `DB_HOST` и `DB_PORT` непосредственно из `.env`. Миграции применяются командой `uv run alembic upgrade head`.

Установить зависимости и запустить тесты:

```text
uv sync
uv run python -m pytest -q
```

Команда с `python -m pytest` запускает тесты из корня проекта и позволяет импортировать локальный пакет `app`.

Запустить API без Docker при доступной базе можно командой `uv run uvicorn app.main:app --reload`.

## Текущее ограничение

В API пока нет авторизации: доступ к созданию и удалению мониторов имеет любой клиент, которому доступен опубликованный порт. Для размещения за пределами локальной машины ограничьте доступ к API; в серверной конфигурации проект публикуется на `127.0.0.1:8000` за обратным прокси Caddy.
