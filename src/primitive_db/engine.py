#!/usr/bin/env python3
"""
Модуль engine - ядро приложения, отвечает за запуск и парсинг команд.
"""

import shlex

from prettytable import PrettyTable

from . import core, parser, utils


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Операции с данными***")
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
    
    print("\nОбщие команды:")
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
        return "", [f"Ошибка парсинга: {e}"]


def parse_insert_command(args):
    """Парсит команду INSERT."""
    if len(args) < 4 or args[0].lower() != "into":
        return None, None
    
    table_name = args[1]
    values_str = " ".join(args[2:])
    values = parser.parse_values(values_str)
    
    return table_name, values


def parse_select_command(args):
    """Парсит команду SELECT."""
    if len(args) < 2 or args[0].lower() != "from":
        return None, None
    
    table_name = args[1]
    
    if len(args) > 3 and args[2].lower() == "where":
        where_str = " ".join(args[3:])
        where_clause = parser.parse_where_clause(where_str)
        return table_name, where_clause
    
    return table_name, None


def parse_update_command(args):
    """Парсит команду UPDATE."""
    if len(args) < 6:
        return None, None, None
    
    table_name = args[0]
    set_str = ""
    where_str = ""
    found_set = False
    found_where = False
    
    for i, arg in enumerate(args[1:], 1):
        if arg.lower() == "set" and not found_set:
            found_set = True
            continue
        elif arg.lower() == "where" and found_set:
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
    if len(args) < 4 or args[0].lower() != "from" or args[2].lower() != "where":
        return None, None
    
    table_name = args[1]
    where_str = " ".join(args[3:])
    where_clause = parser.parse_where_clause(where_str)
    
    return table_name, where_clause


def print_table_as_prettytable(table_data):
    """Выводит данные в виде PrettyTable."""
    if not table_data:
        print("Нет данных для отображения.")
        return
    
    table = PrettyTable()
    table.field_names = list(table_data[0].keys())
    
    for record in table_data:
        table.add_row([record[col] for col in table.field_names])
    
    print(table)


def run():
    """Главная функция запуска приложения."""
    print("***База данных***")
    print_help()
    
    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
            command, args = parse_command(user_input)
            metadata = utils.load_metadata()
            
            if command == "exit":
                print("Выход из программы...")
                break
                
            elif command == "help":
                print_help()
                
            # Управление таблицами
            elif command == "create_table":
                if len(args) < 2:
                    msg = (
                        "Ошибка: Использование: "
                        "create_table <таблица> <столбец1:тип> ..."
                    )
                    print(msg)
                    continue
                
                metadata, message = core.create_table(
                    metadata, args[0], args[1:]
                )
                print(message)
                
                if "успешно" in message.lower():
                    utils.save_metadata(metadata)
                    utils.save_table_data(args[0], [])
                    
            elif command == "drop_table":
                if len(args) != 1:
                    print("Ошибка: Использование: drop_table <таблица>")
                    continue
                
                metadata, message = core.drop_table(metadata, args[0])
                print(message)
                
                if "успешно" in message.lower():
                    utils.save_metadata(metadata)
                    
            elif command == "list_tables":
                print(core.list_tables(metadata))
                
            # CRUD операции
            elif command == "insert":
                table_name, values = parse_insert_command(args)
                
                if table_name is None:
                    msg = (
                        "Ошибка: Использование: "
                        "insert into <таблица> values (значение1, значение2, ...)"
                    )
                    print(msg)
                    continue
                
                table_data = utils.load_table_data(table_name)
                table_data, message = core.insert(
                    metadata, table_name, values, table_data
                )
                
                print(message)
                if "успешно" in message.lower():
                    utils.save_table_data(table_name, table_data)
                
            elif command == "select":
                table_name, where_clause = parse_select_command(args)
                
                if table_name is None:
                    msg = (
                        "Ошибка: Использование: "
                        "select from <таблица> [where <условие>]"
                    )
                    print(msg)
                    continue
                
                table_data = utils.load_table_data(table_name)
                filtered_data = core.select(table_data, where_clause)
                
                print_table_as_prettytable(filtered_data)
                
            elif command == "update":
                table_name, set_clause, where_clause = parse_update_command(args)
                
                if table_name is None or not set_clause or not where_clause:
                    msg = (
                        "Ошибка: Использование: "
                        "update <таблица> set <столбец>=<значение> where <условие>"
                    )
                    print(msg)
                    continue
                
                table_data = utils.load_table_data(table_name)
                updated_data = core.update(
                    table_data, set_clause, where_clause
                )
                
                utils.save_table_data(table_name, updated_data)
                success_msg = (
                    f'Запись в таблице "{table_name}" '
                    f'успешно обновлена.'
                )
                print(success_msg)
                
            elif command == "delete":
                table_name, where_clause = parse_delete_command(args)
                
                if table_name is None or not where_clause:
                    msg = (
                        "Ошибка: Использование: "
                        "delete from <таблица> where <условие>"
                    )
                    print(msg)
                    continue
                
                table_data = utils.load_table_data(table_name)
                updated_data = core.delete(table_data, where_clause)
                
                utils.save_table_data(table_name, updated_data)
                success_msg = (
                    f'Запись успешно удалена '
                    f'из таблицы "{table_name}".'
                )
                print(success_msg)
                
            elif command == "info":
                if len(args) != 1:
                    print("Ошибка: Использование: info <таблица>")
                    continue
                
                table_name = args[0]
                table_data = utils.load_table_data(table_name)
                info = core.info_table(metadata, table_name, table_data)
                print(info)
                
            elif command == "":
                continue
                
            else:
                print(f"Функции '{command}' нет. Попробуйте снова.")
                print_help()
                
        except KeyboardInterrupt:
            print("\n\nВыход из программы...")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")


def main():
    """Основная функция запуска приложения."""
    run()


if __name__ == "__main__":
    main()