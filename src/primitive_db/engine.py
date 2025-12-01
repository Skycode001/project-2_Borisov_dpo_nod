#!/usr/bin/env python3
"""
Модуль engine - ядро приложения, отвечает за запуск и парсинг команд.
"""

import shlex

from . import core, utils


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
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


def run():
    """Главная функция запуска приложения."""
    print("***База данных***")
    print_help()
    
    while True:
        try:
            # Используем стандартный input вместо проблемного prompt
            user_input = input(">>>Введите команду: ").strip()
            
            # Парсим команду
            command, args = parse_command(user_input)
            
            # Загружаем текущие метаданные
            metadata = utils.load_metadata()
            
            # Обработка команд
            if command == "exit":
                print("Выход из программы...")
                break
                
            elif command == "help":
                print_help()
                
            elif command == "create_table":
                if len(args) < 2:
                    usage_msg = (
                        "Ошибка: Использование: "
                        "create_table <имя_таблицы> <столбец1:тип> ..."
                    )
                    print(usage_msg)
                    print_help()  # Добавляем вывод справки
                    continue
                
                table_name = args[0]
                columns = args[1:]
                
                # Создаем таблицу
                metadata, message = core.create_table(
                    metadata, table_name, columns
                )
                print(message)
                
                # Сохраняем метаданные если успешно
                if "успешно" in message.lower():
                    utils.save_metadata(metadata)
                    
            elif command == "drop_table":
                if len(args) != 1:
                    usage_msg = (
                        "Ошибка: Использование: "
                        "drop_table <имя_таблицы>"
                    )
                    print(usage_msg)
                    print_help()  # Добавляем вывод справки
                    continue
                
                table_name = args[0]
                
                # Удаляем таблицу
                metadata, message = core.drop_table(metadata, table_name)
                print(message)
                
                # Сохраняем метаданные если успешно
                if "успешно" in message.lower():
                    utils.save_metadata(metadata)
                    
            elif command == "list_tables":
                tables_list = core.list_tables(metadata)
                print(tables_list)
                
            elif command == "":
                continue  # Пустая команда - просто продолжаем
                
            else:
                print(f"Функции '{command}' нет. Попробуйте снова.")
                print_help()  # Добавляем вывод справки при некорректной команде
                
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