#!/usr/bin/env python3
"""
Модуль engine - ядро приложения, отвечает за запуск и парсинг команд.
"""

import shlex

from prettytable import PrettyTable

from . import core, parser, utils
from .decorators import create_cacher

# Константы для устранения "магических чисел" и строк
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

# Команды для проверки в парсерах
INSERT_KEYWORD = "into"
SELECT_KEYWORD = "from"
UPDATE_SET_KEYWORD = "set"
UPDATE_WHERE_KEYWORD = "where"
DELETE_FROM_KEYWORD = "from"
DELETE_WHERE_KEYWORD = "where"

# Минимальное количество аргументов для команд
MIN_INSERT_ARGS = 4
MIN_SELECT_ARGS = 2
MIN_UPDATE_ARGS = 6
MIN_DELETE_ARGS = 4

# Сообщения об ошибках использования
CREATE_TABLE_USAGE = "create_table <таблица> <столбец1:тип> ..."
DROP_TABLE_USAGE = "drop_table <таблица>"
INSERT_USAGE = "insert into <таблица> values (значение1, значение2, ...)"
SELECT_USAGE = "select from <таблица> [where <условие>]"
UPDATE_USAGE = "update <таблица> set <столбец>=<значение> where <условие>"
DELETE_USAGE = "delete from <таблица> where <условие>"
INFO_USAGE = "info <таблица>"

# Создаем кэшер для результатов запросов
cache_result = create_cacher()


def clear_table_cache(table_name):
    """Очищает кэш для конкретной таблицы."""
    if hasattr(cache_result, '__closure__') and cache_result.__closure__:
        cache_dict = cache_result.__closure__[0].cell_contents
        keys_to_remove = [
            key for key in cache_dict.keys()
            if key.startswith(f"{table_name}{CACHE_KEY_SEPARATOR}")
        ]
        for key in keys_to_remove:
            cache_dict.pop(key, None)


def print_help():
    """Prints the help message for the current mode."""
    print(HELP_TITLE)
    print("Функции:")
    
    # Команды управления таблицами
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    # CRUD операции
    insert_desc = (
        "<command> insert into <имя_таблицы> "
        "values (<значение1>, <значение2>, ...) - создать запись."
    )
    print(insert_desc)
    
    select_desc = (
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print(select_desc)
    
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    
    update_desc = (
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(update_desc)
    
    delete_desc = (
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print(delete_desc)
    
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    
    print(GENERAL_COMMANDS_TITLE)
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_command(command_str):
    """
    Парсит команду пользователя.
    
    Args:
        command_str: Введенная пользователем строка
        
    Returns:
        tuple: (команда, аргументы)
    """
    if not command_str.strip():
        return "", []
    
    try:
        parts = shlex.split(command_str)
        return parts[0], parts[1:]
    except ValueError as e:
        return "", [PARSE_ERROR_MESSAGE.format(e)]


def parse_insert_command(args):
    """Парсит команду INSERT."""
    if len(args) < MIN_INSERT_ARGS or args[0].lower() != INSERT_KEYWORD:
        return None, None
    
    table_name = args[1]
    values_str = " ".join(args[2:])
    values = parser.parse_values(values_str)
    
    return table_name, values


def parse_select_command(args):
    """Парсит команду SELECT."""
    if len(args) < MIN_SELECT_ARGS or args[0].lower() != SELECT_KEYWORD:
        return None, None
    
    table_name = args[1]
    
    if len(args) > 3 and args[2].lower() == UPDATE_WHERE_KEYWORD:
        where_str = " ".join(args[3:])
        where_clause = parser.parse_where_clause(where_str)
        return table_name, where_clause
    
    return table_name, None


def parse_update_command(args):
    """Парсит команду UPDATE."""
    if len(args) < MIN_UPDATE_ARGS:
        return None, None, None
    
    table_name = args[0]
    set_str = ""
    where_str = ""
    found_set = False
    found_where = False
    
    for i, arg in enumerate(args[1:], 1):
        if arg.lower() == UPDATE_SET_KEYWORD and not found_set:
            found_set = True
            continue
        elif arg.lower() == UPDATE_WHERE_KEYWORD and found_set:
            found_where = True
            continue
        
        if found_set and not found_where:
            set_str += f" {arg}"
        elif found_where:
            where_str += f" {arg}"
    
    if not found_set:
        return None, None, None
    
    set_clause = parser.parse_set_clause(set_str.strip())
    where_clause = parser.parse_where_clause(where_str.strip())
    
    return table_name, set_clause, where_clause


def parse_delete_command(args):
    """Парсит команду DELETE."""
    if (len(args) < MIN_DELETE_ARGS or 
        args[0].lower() != DELETE_FROM_KEYWORD or 
        args[2].lower() != DELETE_WHERE_KEYWORD):
        return None, None
    
    table_name = args[1]
    where_str = " ".join(args[3:])
    where_clause = parser.parse_where_clause(where_str)
    
    return table_name, where_clause


def print_table_as_prettytable(table_data):
    """Выводит данные в виде PrettyTable."""
    if not table_data:
        print(NO_DATA_MESSAGE)
        return
    
    table = PrettyTable()
    table.field_names = list(table_data[0].keys())
    
    for record in table_data:
        table.add_row([record[col] for col in table.field_names])
    
    print(table)


def run():
    """Главная функция запуска приложения."""
    print(DB_TITLE)
    print_help()
    
    while True:
        try:
            user_input = input(COMMAND_PROMPT).strip()
            command, args = parse_command(user_input)
            metadata = utils.load_metadata()
            
            if command == "exit":
                print(EXIT_MESSAGE)
                break
                
            elif command == "help":
                print_help()
                
            # Управление таблицами
            elif command == "create_table":
                if len(args) < 2:
                    msg = f"Ошибка: Использование: {CREATE_TABLE_USAGE}"
                    print(msg)
                    continue
                
                metadata, message = core.create_table(
                    metadata, args[0], args[1:]
                )
                print(message)
                
                if SUCCESS_INDICATOR in message.lower():
                    utils.save_metadata(metadata)
                    utils.save_table_data(args[0], [])
                    
            elif command == "drop_table":
                if len(args) != 1:
                    print(f"Ошибка: Использование: {DROP_TABLE_USAGE}")
                    continue

                result = core.drop_table(metadata, args[0])

                if isinstance(result, tuple) and len(result) == 2:
                    metadata, message = result

                    # Выводим сообщение только если не "Операция отменена."
                    if CANCELLED_INDICATOR not in message.lower():
                        print(message)
                    
                    if SUCCESS_INDICATOR in message.lower():
                        utils.save_metadata(metadata)
                        clear_table_cache(args[0])
                    
            elif command == "list_tables":
                print(core.list_tables(metadata))
                
            # CRUD операции
            elif command == "insert":
                table_name, values = parse_insert_command(args)
                
                if table_name is None:
                    msg = f"Ошибка: Использование: {INSERT_USAGE}"
                    print(msg)
                    continue
                
                table_data = utils.load_table_data(table_name)
                table_data, message = core.insert(
                    metadata, table_name, values, table_data
                )
                
                print(message)
                if SUCCESS_INDICATOR in message.lower():
                    utils.save_table_data(table_name, table_data)
                    clear_table_cache(table_name)
                
            elif command == "select":
                table_name, where_clause = parse_select_command(args)
                
                if table_name is None:
                    msg = f"Ошибка: Использование: {SELECT_USAGE}"
                    print(msg)
                    continue
                
                # Запросы без условия НЕ кэшируем
                if where_clause is None:
                    table_data = utils.load_table_data(table_name)
                    filtered_data = core.select(table_data, where_clause)
                else:
                    # Кэшируем только запросы с условиями
                    cache_key = f"{table_name}{CACHE_KEY_SEPARATOR}{str(where_clause)}"
                    
                    def execute_select():
                        table_data = utils.load_table_data(table_name)
                        return core.select(table_data, where_clause)
                    
                    filtered_data = cache_result(cache_key, execute_select)
                
                print_table_as_prettytable(filtered_data)
                
            elif command == "update":
                table_name, set_clause, where_clause = parse_update_command(args)
                
                if table_name is None or not set_clause or not where_clause:
                    msg = f"Ошибка: Использование: {UPDATE_USAGE}"
                    print(msg)
                    continue
                
                table_data = utils.load_table_data(table_name)
                updated_data = core.update(
                    table_data, set_clause, where_clause
                )

                utils.save_table_data(table_name, updated_data)
                clear_table_cache(table_name)
                success_msg = (
                    f'Запись в таблице "{table_name}" '
                    f'успешно обновлена.'
                )
                print(success_msg)
                
            elif command == "delete":
                table_name, where_clause = parse_delete_command(args)
                
                if table_name is None or not where_clause:
                    msg = f"Ошибка: Использование: {DELETE_USAGE}"
                    print(msg)
                    continue
                
                table_data = utils.load_table_data(table_name)
                result = core.delete(table_data, where_clause)
                
                utils.save_table_data(table_name, result)
                clear_table_cache(table_name)

                if len(result) < len(table_data):
                    success_msg = (
                        f'Запись успешно удалена '
                        f'из таблицы "{table_name}".'
                    )
                    print(success_msg)
                
            elif command == "info":
                if len(args) != 1:
                    print(f"Ошибка: Использование: {INFO_USAGE}")
                    continue
                
                table_name = args[0]
                table_data = utils.load_table_data(table_name)
                info = core.info_table(metadata, table_name, table_data)
                print(info)
                
            elif command == "":
                continue
                
            else:
                print(UNKNOWN_COMMAND_MESSAGE.format(command))
                print_help()
                
        except KeyboardInterrupt:
            print(INTERRUPT_MESSAGE)
            break
        except Exception as e:
            print(UNEXPECTED_ERROR_MESSAGE.format(e))


def main():
    """Основная функция запуска приложения."""
    run()


if __name__ == "__main__":
    main()