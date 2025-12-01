#!/usr/bin/env python3
"""
Основная логика работы с таблицами и данными.
"""

from prettytable import PrettyTable


def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу в метаданных.
    
    Args:
        metadata: Текущие метаданные БД
        table_name: Имя таблицы
        columns: Список столбцов в формате "имя:тип"
        
    Returns:
        tuple: (обновленные метаданные, сообщение об ошибке или успехе)
    """
    # Проверяем что имя таблицы не пустое
    if not table_name or not table_name.strip():
        error_msg = "Ошибка: Имя таблицы не может быть пустым."
        return metadata, error_msg
    
    # Проверяем существование таблицы
    if table_name in metadata:
        error_msg = f'Ошибка: Таблица "{table_name}" уже существует.'
        return metadata, error_msg
    
    # Проверяем что есть хотя бы один столбец кроме ID
    if not columns:
        error_msg = (
            'Ошибка: Таблица должна содержать хотя бы один столбец '
            '(кроме автоматического ID:int).'
        )
        return metadata, error_msg
    
    # Добавляем столбец ID:int в начало
    all_columns = ["ID:int"] + columns
    
    # Проверяем корректность типов и форматов
    valid_types = {"int", "str", "bool"}
    
    for column in all_columns:
        # Проверяем формат "имя:тип"
        if ':' not in column:
            error_msg = (
                f'Некорректный формат столбца: {column}. '
                f'Используйте формат "имя:тип"'
            )
            return metadata, error_msg
        
        # Разделяем имя и тип
        try:
            col_name, col_type = column.split(':', 1)
        except ValueError:
            error_msg = f'Некорректный формат столбца: {column}'
            return metadata, error_msg
        
        # Проверяем что имя столбца не пустое
        if not col_name.strip():
            error_msg = f'Имя столбца не может быть пустым в: {column}'
            return metadata, error_msg
        
        # Проверяем что тип столбца корректен
        if col_type not in valid_types:
            error_msg = (
                f'Неподдерживаемый тип данных: {col_type} в столбце {col_name}. '
                f'Используйте int, str, bool.'
            )
            return metadata, error_msg
        
        # Проверяем дубликаты имен столбцов (кроме ID)
        if column != "ID:int":
            column_names = [c.split(':')[0] for c in all_columns]
            if column_names.count(col_name) > 1:
                error_msg = f'Дублирующееся имя столбца: {col_name}'
                return metadata, error_msg
    
    # Добавляем таблицу в метаданные
    metadata[table_name] = all_columns
    
    # Формируем сообщение об успехе
    columns_str = ", ".join(all_columns)
    success_msg = (
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {columns_str}'
    )
    return metadata, success_msg


def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.
    
    Args:
        metadata: Текущие метаданные БД
        table_name: Имя таблицы для удаления
        
    Returns:
        tuple: (обновленные метаданные, сообщение об ошибке или успехе)
    """
    # Проверяем что имя таблицы не пустое
    if not table_name or not table_name.strip():
        error_msg = "Ошибка: Имя таблицы не может быть пустым."
        return metadata, error_msg
    
    # Проверяем существование таблицы
    if table_name not in metadata:
        error_msg = f'Ошибка: Таблица "{table_name}" не существует.'
        return metadata, error_msg
    
    # Удаляем таблицу
    del metadata[table_name]
    success_msg = f'Таблица "{table_name}" успешно удалена.'
    return metadata, success_msg


def list_tables(metadata):
    """
    Возвращает форматированный список всех таблиц с помощью PrettyTable.
    
    Args:
        metadata: Текущие метаданные БД
        
    Returns:
        str: Форматированная таблица с таблицами и их столбцами
    """
    if not metadata:
        return "Нет созданных таблиц."
    
    table = PrettyTable()
    table.field_names = ["Таблица", "Столбцы"]
    table.align = "l"
    
    for table_name, columns in metadata.items():
        columns_str = ", ".join(columns)
        table.add_row([table_name, columns_str])
    
    return table