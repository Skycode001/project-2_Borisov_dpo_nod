#!/usr/bin/env python3
"""
Константы для устранения "магических чисел" и строк в проекте.
"""

# Константы для работы с таблицами - core.py
DEFAULT_ID_COLUMN = "ID:int"
VALID_DATA_TYPES = {"int", "str", "bool"}
BOOLEAN_TRUE_VALUES = ['true', '1', 'yes']
BOOLEAN_FALSE_VALUES = ['false', '0', 'no']
DEFAULT_START_ID = 1

# Сообщения об ошибках и успехах - core.py
EMPTY_TABLE_MESSAGE = "Нет созданных таблиц."
EMPTY_TABLE_ERROR = "Ошибка: Имя таблицы не может быть пустым."
TABLE_EXISTS_ERROR = 'Ошибка: Таблица "{}" уже существует.'
MIN_COLUMNS_ERROR = "Ошибка: Таблица должна содержать хотя бы один столбец."
COLUMN_FORMAT_ERROR = 'Некорректный формат столбца: {}. Используйте "имя:тип"'
EMPTY_COLUMN_NAME_ERROR = "Имя столбца не может быть пустым в: {}"
INVALID_TYPE_ERROR = 'Неподдерживаемый тип данных: {}. Используйте int, str, bool.'
TABLE_NOT_FOUND_ERROR = 'Ошибка: Таблица "{}" не существует.'
SUCCESS_CREATE_MESSAGE = 'Таблица "{}" успешно создана со столбцами: {}'
SUCCESS_DROP_MESSAGE = 'Таблица "{}" успешно удалена.'
VALUES_COUNT_ERROR = "Ошибка: Ожидается {} значений, получено {}."
BOOL_TYPE_ERROR = 'Ошибка: Столбец "{}" ожидает bool, получено {}'
UNSUPPORTED_TYPE_ERROR = "Неподдерживаемый тип: {}"
INVALID_TYPE_FOR_COLUMN_ERROR = 'Ошибка: Неверный тип для столбца {}: {}'
SUCCESS_INSERT_MESSAGE = 'Запись с ID={} успешно добавлена в таблицу "{}".'
INFO_TEMPLATE = "Таблица: {}\nСтолбцы: {}\nКоличество записей: {}"



# Константы для устранения "магических чисел" и строк - engine.py
DB_TITLE = "***База данных***"
COMMAND_PROMPT = ">>>Введите команду: "
EXIT_MESSAGE = "Выход из программы..."
CACHE_KEY_SEPARATOR = "_"
CANCELLED_INDICATOR = "отменена"
SUCCESS_INDICATOR = "успешно"
YES_RESPONSE = "y"
HELP_TITLE = "\n***Операции с данными***"
GENERAL_COMMANDS_TITLE = "\nОбщие команды:"
UNKNOWN_COMMAND_MESSAGE = "Функции '{}' нет. Попробуйте снова."
PARSE_ERROR_MESSAGE = "Ошибка парсинга: {}"
UNEXPECTED_ERROR_MESSAGE = "Произошла ошибка: {}"
NO_DATA_MESSAGE = "Нет данных для отображения."
INTERRUPT_MESSAGE = "\n\nВыход из программы..."

# Команды для проверки в парсерах - engine.py
INSERT_KEYWORD = "into"
SELECT_KEYWORD = "from"
UPDATE_SET_KEYWORD = "set"
UPDATE_WHERE_KEYWORD = "where"
DELETE_FROM_KEYWORD = "from"
DELETE_WHERE_KEYWORD = "where"

# Минимальное количество аргументов для команд - engine.py
MIN_INSERT_ARGS = 4
MIN_SELECT_ARGS = 2
MIN_UPDATE_ARGS = 6
MIN_DELETE_ARGS = 4

# Сообщения об ошибках использования - engine.py
CREATE_TABLE_USAGE = "create_table <таблица> <столбец1:тип> ..."
DROP_TABLE_USAGE = "drop_table <таблица>"
INSERT_USAGE = "insert into <таблица> values (значение1, значение2, ...)"
SELECT_USAGE = "select from <таблица> [where <условие>]"
UPDATE_USAGE = "update <таблица> set <столбец>=<значение> where <условие>"
DELETE_USAGE = "delete from <таблица> where <условие>"
INFO_USAGE = "info <таблица>"


# Константы для устранения "магических строк" - decorators.py
CONFIRMATION_PROMPT_TEMPLATE = 'Вы уверены, что хотите выполнить "{}"? [y/n]: '
CANCELLATION_MESSAGE = "Операция отменена."
UNEXPECTED_ERROR_MESSAGE = "Произошла непредвиденная ошибка: {}"
VALIDATION_ERROR_MESSAGE = "Ошибка валидации: {}"
KEY_ERROR_MESSAGE = "Ошибка: Таблица или столбец {} не найден."
FILE_NOT_FOUND_MESSAGE = (
    "Ошибка: Файл данных не найден. "
    "Возможно, база данных не инициализирована."
)
TIME_FORMAT_TEMPLATE = "Функция {} выполнилась за {:.3f} секунд."

# Константы для устранения "магических чисел" и строк - utils.py
META_FILE = "db_meta.json"
DATA_DIR = "data"
DEFAULT_ENCODING = "utf-8"