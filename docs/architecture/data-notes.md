# ЛР 4А — данные TutBerry

## Соответствие модели ЛР 2Г

| Модель ЛР 2Г | Текущая схема | Решение |
|---|---|---|
| USERS | Django auth_user и UUID идентификаторы владельца/арендатора | Упрощение MVP; полноценная таблица профилей пока не реализована |
| LISTINGS | tutberry_listingrecord | Реализованы основные поля; описание, категория, календарь ещё не перенесены |
| BOOKINGS | tutberry_bookingrecord | Даты включительно, стоимость и залог хранятся в записи |
| LISTING_AVAILABILITY, TRANSACTIONS, MESSAGES, REVIEWS | Нет | Отложено; не считать ЛР 4А полностью завершённой |

## Ручной SQL и ограничения

Миграция `tutberry/migrations/0002_booking_no_overlap.py` применяет `btree_gist` и PostgreSQL `EXCLUDE USING gist`. Для одного объявления диапазоны `daterange(start_date, end_date + 1, '[)')` не должны пересекаться, если статус не `cancelled`. При этом два соседних календарных дня допустимы, а совпадающий день — конфликт: `RentalPeriod` в предметной модели включает обе границы.

В ЛР 3 сценарий `BookingService` зависит от интерфейса. В ЛР 4 добавлен `SqlBookingRepository` с параметризованными SQL-запросами через Django connection; ORM для операций бронирования не используется. Транзакцией и блокировкой объявления владеет обработчик API. Это адаптация методички к согласованному Django, а не реализация её асинхронного `asyncpg`-примера.

## Проверка

В CI `.github/workflows/lab04-ci.yml` выполняются три цикла применения/отката миграции 0002, затем тесты на PostgreSQL. Локально:

```powershell
docker compose up --build -d
docker compose exec api python manage.py showmigrations tutberry
docker compose exec api python manage.py migrate tutberry 0001
docker compose exec api python manage.py migrate
docker compose exec api pytest -q
```

Последняя команда потребует dev-зависимостей внутри контейнера; в стандартном production-образе они могут отсутствовать. Проверка CI является основным тестовым прогоном.

## Ограничения

Для полного зачёта по методичке остаются перенос остальных сущностей из модели ЛР 2Г, индексы с измерением EXPLAIN ANALYZE, expand–contract, отдельное архитектурное решение и дополнительные интеграционные проверки. Не следует считать эти пункты выполненными.
