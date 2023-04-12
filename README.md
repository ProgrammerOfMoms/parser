# Описание задания

## Обязательные требования
Важно: задание дается на проверку у вас определенных знаний и умений, при выполнении задания уделите
внимание оформлению и архитектуре кода. Выполненное задание должно сопровождаться тестами.
Выбор сторонних библиотек, при необходимости, остается за разработчиком, при выборе той или иной библиотеки дать
обоснование.

## Суть задания
Необходимо разработать сервис, для разбора входящего csv файла в директорию и базу данных.

## Требования
Каждые 2 минуты (+- 30сек) в папку &#39;In&#39; файловой системы поступает файл в формате csv, все поля обязательные имя файла в
формате &#39;20221129_1234_DME.csv&#39; - &#39;&lt;год&gt;&lt;месяц&gt;&lt;день&gt;_&lt;номер рейса&gt;_&lt;аэропорт вылета&gt;.csv&#39;
При появлении файла (Приложение 1) в папке нужно преобразовать файл в формат json (Приложение 2) и сохранить его в
папке &#39;Out&#39;. Исходный файл переместить в папку &#39;Ok&#39;. В случае возникновения ошибок файл переместить в папку &#39;Err&#39;.
Успешно обработанные файлы поместить в таблицу &#39;flight&#39;(Приложение 3) базы данных SQLite (или другую на выбор).

## Дополнительные требования
- Процессы сохранения файла в папку и в БД желательно сделать параллельными.
- Базу данных и таблицу flight создать при первом запуске программы
- Все действия сервиса должны выводиться в лог
- Реализовать REST API метод для выборки всех рейсов из таблицы flight за определённую дату
- Ответить на вопрос: каким образом можно ускорить запрос на выборку данных, при большом объеме данных.


## Используемые библиотеки
- FastApi - для предоставления API.

Причина выбора: Быстрый фреймворк, автоматическая документация, лаконичность, обязательность аннотаций
- Celery - для выполнения переодических задач.

Причина выбора: Поддерживаемая, легко масштабируемая очередь задач.
- SqlAlchemy - как ОРМ.

Причина выбора: Безопасность, производительность, переносимость.
### Дополнительные библиотеки
- Alembic - для миграций БД.
- Mypy - проверка аннотаций
- Pytest - для тестирования функционала.

## Структура
Директории In, Out, Err, Ok находятся в директории project_dir/app/files

## Запуск
1. Клонировать репозиторий
2. Установить докер
3. Заполнить файлик .env в корне или переименовать test_env в .env
4. Запустить контейнер docker compose up -d --build

### Запуск тестов
docker compose exec parser pytest

## Swagger документация
Доступна по адресу: localhost:8000/docs

## Логгирование
Логирование осуществляется в stdout и файлы (project_dir/logs/)\n

Уровень логгирования определяется переменной окружения LOG_LEVEL

## Дополнительно
При состоянии переменной окружения DEBUG = True, поднимается дополнительная задача в Celery, которая раз в TASK_GENERATE_FILE_SEC генерирует новый входящий файл.

Если DEBUG = False (по умолчанию), то поднимается только задача обработки входящих файлов раз в TASK_PROCESS_INCOMING_FILES_SEC секунд.