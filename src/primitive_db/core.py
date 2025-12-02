#!/usr/bin/env python3
"""
Основная логика работы с таблицами и данными.
"""

from prettytable import PrettyTable

from .constants import (
    BOOL_TYPE_ERROR,
    BOOLEAN_FALSE_VALUES,
    BOOLEAN_TRUE_VALUES,
    COLUMN_FORMAT_ERROR,
    DEFAULT_ID_COLUMN,
    DEFAULT_START_ID,
    EMPTY_COLUMN_NAME_ERROR,
    EMPTY_TABLE_ERROR,
    EMPTY_TABLE_MESSAGE,
    INFO_TEMPLATE,
    INVALID_TYPE_ERROR,
    INVALID_TYPE_FOR_COLUMN_ERROR,
    MIN_COLUMNS_ERROR,
    SUCCESS_CREATE_MESSAGE,
    SUCCESS_DROP_MESSAGE,
    SUCCESS_INSERT_MESSAGE,
    TABLE_EXISTS_ERROR,
    TABLE_NOT_FOUND_ERROR,
    UNSUPPORTED_TYPE_ERROR,
    VALID_DATA_TYPES,
    VALUES_COUNT_ERROR,
)
from .decorators import confirm_action, handle_db_errors, log_time


@handle_db_errors
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
    if not table_name or not table_name.strip():
        return metadata, EMPTY_TABLE_ERROR
    
    if table_name in metadata:
        return metadata, TABLE_EXISTS_ERROR.format(table_name)
    
    if not columns:
        return metadata, MIN_COLUMNS_ERROR
    
    all_columns = [DEFAULT_ID_COLUMN] + columns
    
    for column in all_columns:
        if ':' not in column:
            return metadata, COLUMN_FORMAT_ERROR.format(column)
        
        col_name, col_type = column.split(':', 1)
        
        if not col_name.strip():
            return metadata, EMPTY_COLUMN_NAME_ERROR.format(column)
        
        if col_type not in VALID_DATA_TYPES:
            return metadata, INVALID_TYPE_ERROR.format(col_type)
    
    metadata[table_name] = all_columns
    columns_str = ", ".join(all_columns)
    
    return metadata, SUCCESS_CREATE_MESSAGE.format(table_name, columns_str)


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.
    
    Args:
        metadata: Текущие метаданные БД
        table_name: Имя таблицы для удаления
        
    Returns:
        tuple: (обновленные метаданные, сообщение) или (metadata, "Отменено")
    """
    # Если функция вызвалась - значит подтверждение получено
    if not table_name or not table_name.strip():
        return metadata, EMPTY_TABLE_ERROR
    
    if table_name not in metadata:
        return metadata, TABLE_NOT_FOUND_ERROR.format(table_name)
    
    del metadata[table_name]
    return metadata, SUCCESS_DROP_MESSAGE.format(table_name)


@handle_db_errors
def list_tables(metadata):
    """
    Возвращает форматированный список всех таблиц.
    
    Args:
        metadata: Текущие метаданные БД
        
    Returns:
        str: Форматированная таблица с таблицами и их столбцами
    """
    if not metadata:
        return EMPTY_TABLE_MESSAGE
    
    table = PrettyTable()
    table.field_names = ["Таблица", "Столбцы"]
    table.align = "l"
    
    for table_name, columns in metadata.items():
        columns_str = ", ".join(columns)
        table.add_row([table_name, columns_str])
    
    return table


@handle_db_errors
def info_table(metadata, table_name, table_data):
    """
    Выводит информацию о таблице.
    
    Args:
        metadata: Метаданные БД
        table_name: Имя таблицы
        table_data: Данные таблицы
        
    Returns:
        str: Информация о таблице
    """
    if table_name not in metadata:
        return TABLE_NOT_FOUND_ERROR.format(table_name)
    
    columns = metadata[table_name]
    columns_str = ", ".join(columns)
    record_count = len(table_data)
    
    return INFO_TEMPLATE.format(table_name, columns_str, record_count)


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """
    Вставляет запись в таблицу.
    
    Args:
        metadata: Метаданные БД
        table_name: Имя таблицы
        values: Список значений для вставки
        table_data: Текущие данные таблицы
        
    Returns:
        tuple: (обновленные данные таблицы, сообщение об ошибке или успехе)
    """
    if table_name not in metadata:
        return table_data, TABLE_NOT_FOUND_ERROR.format(table_name)
    
    columns_spec = metadata[table_name]
    data_columns = columns_spec[1:]  # Пропускаем ID:int
    
    if len(values) != len(data_columns):
        expected = len(data_columns)
        actual = len(values)
        return table_data, VALUES_COUNT_ERROR.format(expected, actual)
    
    # Валидируем и преобразуем значения
    validated_values = []
    for i, (col_spec, value) in enumerate(zip(data_columns, values)):
        col_name, col_type = col_spec.split(':')
        
        try:
            if col_type == 'int':
                validated_values.append(int(value))
            elif col_type == 'str':
                # Убираем кавычки если есть
                if isinstance(value, str) and (
                    (value.startswith('"') and value.endswith('"')) or
                    (value.startswith("'") and value.endswith("'"))
                ):
                    validated_values.append(value[1:-1])
                else:
                    validated_values.append(str(value))
            elif col_type == 'bool':
                if isinstance(value, bool):
                    validated_values.append(value)
                elif isinstance(value, str):
                    if value.lower() in BOOLEAN_TRUE_VALUES:
                        validated_values.append(True)
                    elif value.lower() in BOOLEAN_FALSE_VALUES:
                        validated_values.append(False)
                    else:
                        return table_data, BOOL_TYPE_ERROR.format(col_name, value)
                elif isinstance(value, int):
                    validated_values.append(bool(value))
                else:
                    return table_data, BOOL_TYPE_ERROR.format(col_name, value)
            else:
                return table_data, UNSUPPORTED_TYPE_ERROR.format(col_type)
        except (ValueError, TypeError):
            return table_data, INVALID_TYPE_FOR_COLUMN_ERROR.format(col_name, value)
    
    # Генерируем ID
    next_id = DEFAULT_START_ID
    if table_data:
        ids = [record.get("ID", 0) for record in table_data]
        next_id = max(ids) + 1 if ids else DEFAULT_START_ID
    
    # Создаем запись
    record = {"ID": next_id}
    for col_spec, value in zip(data_columns, validated_values):
        col_name, _ = col_spec.split(':')
        record[col_name] = value
    
    # Добавляем в данные
    table_data.append(record)
    
    return table_data, SUCCESS_INSERT_MESSAGE.format(next_id, table_name)


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """
    Выбирает записи из таблицы.
    """
    if not table_data:
        return []
    
    if where_clause is None:
        return table_data
    
    column, value = next(iter(where_clause.items()))
    value_str = str(value).lower()  # Приводим к нижнему регистру
    
    filtered_data = [
        record for record in table_data 
        if str(record.get(column, "")).lower() == value_str
    ]
    
    return filtered_data


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """
    Обновляет записи в таблицы.
    
    Args:
        table_data: Данные таблицы
        set_clause: Что обновить
        where_clause: Условие для поиска записей
        
    Returns:
        list: Обновленные данные таблицы
    """
    if not table_data or not set_clause or not where_clause:
        return table_data
    
    set_column, new_value = next(iter(set_clause.items()))
    where_column, where_value = next(iter(where_clause.items()))
    
    # Приводим к нижнему регистру для сравнения
    where_value_str = str(where_value).lower()
    updated_count = 0
    
    for record in table_data:
        # Тоже приводим к нижнему регистру
        record_value = str(record.get(where_column, "")).lower()
        if record_value == where_value_str:
            record[set_column] = new_value
            updated_count += 1
    
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """
    Удаляет записи из таблицы.
    """
    if not table_data or not where_clause:
        return table_data
    
    column, value = next(iter(where_clause.items()))
    value_str = str(value).lower()  # Приводим к нижнему регистру для поиска
    
    filtered_data = [
        record for record in table_data 
        if str(record.get(column, "")).lower() != value_str
    ]
    
    return filtered_data