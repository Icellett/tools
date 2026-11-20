# План-график разработки (Диаграмма Ганта)

Ниже представлен план разработки MVP (Minimum Viable Product) маркетплейса аренды инструментов. 
Проект разбит на 5 основных этапов: от проектирования архитектуры до запуска.

```mermaid
gantt
    title План разработки MVP «TutBerry»
    dateFormat  YYYY-MM-DD
    axisFormat  %d.%m
    
    section Аналитика и Дизайн
    Сбор требований и CJM/USM         :done,    des1, 2026-23-10, 7d
    Проектирование ER-модели и API    :done,    des2, after des1, 5d
    Дизайн UI/UX (Web, Mobile)        :active,  des3, after des1, 10d
    
    section Бэкенд (Backend)
    Настройка инфраструктуры (Docker):         dev1, after des2, 3d
    Модуль авторизации и профилей     :         dev2, after dev1, 5d
    Модуль объявлений и календаря     :         dev3, after dev2, 7d
    Модуль бронирования и статусов    :         dev4, after dev3, 7d
    Интеграция платежей (Эскроу)      :         dev5, after dev4, 8d
    Модуль отзывов и рейтингов        :         dev6, after dev5, 4d
    Панель модератора (Споры)         :         dev7, after dev6, 5d
    
    section Фронтенд (Frontend)
    Верстка базовых экранов           :         front1, after des3, 7d
    Личный кабинет (Владелец/Арендатор):        front2, after front1, 8d
    Интеграция с API поиска и брони   :         front3, after front2, 7d
    Экран оплаты и чата               :         front4, after front3, 5d
    Админ-панель (Платформа)          :         front5, after front4, 4d
    
    section Тестирование и Релиз
    Написание автотестов (API)        :         test1, after dev4, 10d
    Ручное тестирование (QA)          :         test2, after front4, 7d
    Нагрузочное тестирование (NFR-01) :         test3, after test2, 3d
    Исправление багов (Bug fixing)    :         test4, after test3, 4d
    Деплой на прод и запуск MVP       :milestone, m1, after test4, 0d
