# ЛР 3 — реализация сервиса TutBerry (Django)

## Выбор технологий

Согласно ADR-0002 используется Python 3.13, Django REST Framework и PostgreSQL 17. В методических примерах указан FastAPI; выбор Django нужно согласовать с преподавателем.

## ЛР 3А — первый работающий сервис

- `GET /health` возвращает `{"status":"ok"}`.
- `GET /version` возвращает версию приложения и название окружения.
- Конфигурация берётся из переменных окружения, обязательные значения валидируются при старте.
- Middleware создаёт структурированные JSON-логи и передаёт `X-Request-Id`.
- Dockerfile и `compose.yaml` запускают API и PostgreSQL.
- Добавлены проверки Django, миграций, API и сборки Docker в GitHub Actions.

## ЛР 3Б — предметная логика

Реализованы независимые от Django агрегаты `Listing`, `Booking`, `Payment` и объекты-значения `RentalPeriod`, `BookingPrice`. Сервис `BookingService` использует порты `BookingRepository`, `IdGenerator` и `BookingNotifier`. В HTTP-слое реализован `POST /api/bookings` для авторизованных пользователей. Стоимость берётся из объявления, а не из тела запроса. PostgreSQL-адаптер и транзакционная блокировка записи объявления обеспечивают последовательную проверку конфликтующих бронирований в данном сценарии.

## Локальный запуск на Windows

Требуются Git, Docker Desktop и включённая виртуализация / WSL 2.

```powershell
git clone -b lab-03 https://github.com/TutBerry/tools.git
cd tools
Copy-Item .env.example .env
docker compose up --build -d
```

Проверить:

```powershell
curl.exe -i http://127.0.0.1:8080/health
curl.exe -i http://127.0.0.1:8080/version
docker compose logs --tail=50 api
```

Остановка: `docker compose down`. Данные PostgreSQL сохраняются в томе `pgdata`. Для локальной демонстрации используются тестовые секреты из `compose.yaml`; перед реальным развёртыванием их необходимо заменить.

## Подтверждённые результаты

21.11.2026 при локальном запуске на Windows пользователь подтвердил:

| Проверка | Результат |
|---|---|
| Docker Compose | API и PostgreSQL запущены |
| PostgreSQL | Контейнер `Healthy` |
| Миграции | `auth`, `contenttypes`, `tutberry.0001_initial` — OK |
| `GET /health` | HTTP 200, `{"status":"ok"}` |
| `GET /version` | HTTP 200, `{"version":"0.1.0","environment":"production"}` |
| GitHub Actions: Django, миграции и тесты | Успешно, запуск [№ 38](https://github.com/TutBerry/tools/actions/runs/44868425892) |

При проверке браузером обнаружена ошибка 500: Django REST Framework пытался вывести HTML-представление без настроенного шаблонизатора. Исправлено включением `DjangoTemplates` в `tutberry/settings.py`; повторная проверка `/health` в браузере показала HTTP 200.

## Ограничения

Демонстрационная реализация не включает полноценные сценарии оплаты, уведомлений и модерации через API. Не проведены нагрузочные тесты и проверка реальных платежей. Для сдачи преподавателю следует отдельно подтвердить допустимость Django вместо FastAPI.
