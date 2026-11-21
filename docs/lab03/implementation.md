# ЛР 3 — реализация на Django

Сохранено решение ADR-0002: Django REST Framework вместо FastAPI. Это осознанное отклонение от примеров методички М07–М08, требующее согласования с преподавателем.

## М07: первый сервис

Реализованы `/health`, `/version`, валидация обязательных `DJANGO_SECRET_KEY` и `DATABASE_URL`, JSON-журнал запросов, `X-Request-Id`, Docker Compose с PostgreSQL и тесты HTTP API.

## Запуск

Локально: создать виртуальное окружение, установить `requirements-dev.txt`, скопировать `.env.example` в `.env`, загрузить переменные окружения и выполнить `python manage.py runserver 8080`. Для базы требуется работающий PostgreSQL.

Контейнер: `docker compose up --build`, затем `curl http://localhost:8080/health` и `curl http://localhost:8080/version`.

Тесты: при заданных `DJANGO_SECRET_KEY` и `DATABASE_URL` выполнить `pytest`.

## Дальше

М08: реализация агрегатов `Listing`, `Booking`, `Payment` из `docs/domain/aggregates.md`, тестовые дубли, аудит тестируемости и отчёт о рефакторинге. Полная проверка запуска Docker и CI ещё не выполнена.
