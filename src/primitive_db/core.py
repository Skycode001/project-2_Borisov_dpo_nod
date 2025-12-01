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
    if not table_name or not table_name.strip():
        return metadata, "Ошибка: Имя таблицы не может быть пустым."
    
    if table_name in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" уже существует.'
    
    if not columns:
        return metadata, 'Ошибка: Таблица должна содержать хотя бы один столбец.'
    
    all_columns = ["ID:int"] + columns
    valid_types = {"int", "str", "bool"}
    
    for column in all_columns:
        if ':' not in column:
            msg = f'Некорректный формат столбца: {column}. Используйте "имя:тип"'
            return metadata, msg
        
        col_name, col_type = column.split(':', 1)
        
        if not col_name.strip():
            msg = f'Имя столбца не может быть пустым в: {column}'
            return metadata, msg
        
        if col_type not in valid_types:
            msg = (
                f'Неподдерживаемый тип данных: {col_type}. '
                f'Используйте int, str, bool.'
            )
            return metadata, msg
    
    metadata[table_name] = all_columns
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
    if not table_name or not table_name.strip():
        return metadata, "Ошибка: Имя таблицы не может быть пустым."
    
    if table_name not in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" не существует.'
    
    del metadata[table_name]
    return metadata, f'Таблица "{table_name}" успешно удалена.'


def list_tables(metadata):
    """
    Возвращает форматированный список всех таблиц.
    
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
        return f'Ошибка: Таблица "{table_name}" не существует.'
    
    columns = metadata[table_name]
    columns_str = ", ".join(columns)
    record_count = len(table_data)
    
    return (
        f'Таблица: {table_name}\n'
        f'Столбцы: {columns_str}\n'
        f'Количество записей: {record_count}'
    )


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
        return table_data, f'Ошибка: Таблица "{table_name}" не существует.'
    
    columns_spec = metadata[table_name]
    data_columns = columns_spec[1:]  # Пропускаем ID:int
    
    if len(values) != len(data_columns):
        expected = len(data_columns)
        actual = len(values)
        msg = f'Ошибка: Ожидается {expected} значений, получено {actual}.'
        return table_data, msg
    
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
                    if value.lower() in ['true', '1', 'yes']:
                        validated_values.append(True)
                    elif value.lower() in ['false', '0', 'no']:
                        validated_values.append(False)
                    else:
                        msg = (
                            f'Ошибка: Столбец "{col_name}" '
                            f'ожидает bool, получено {value}'
                        )
                        return table_data, msg
                elif isinstance(value, int):
                    validated_values.append(bool(value))
                else:
                    msg = (
                        f'Ошибка: Столбец "{col_name}" '
                        f'ожидает bool, получено {value}'
                    )
                    return table_data, msg
            else:
                return table_data, f'Неподдерживаемый тип: {col_type}'
        except (ValueError, TypeError):
            msg = f'Ошибка: Неверный тип для столбца {col_name}: {value}'
            return table_data, msg
    
    # Генерируем ID
    next_id = 1
    if table_data:
        ids = [record.get("ID", 0) for record in table_data]
        next_id = max(ids) + 1 if ids else 1
    
    # Создаем запись
    record = {"ID": next_id}
    for col_spec, value in zip(data_columns, validated_values):
        col_name, _ = col_spec.split(':')
        record[col_name] = value
    
    # Добавляем в данные
    table_data.append(record)
    success_msg = (
        f'Запись с ID={next_id} успешно добавлена '
        f'в таблицу "{table_name}".'
    )
    
    return table_data, success_msg


def select(table_data, where_clause=None):
    """
    Выбирает записи из таблицы.
    
    Args:
        table_data: Данные таблицы
        where_clause: Условие фильтрации или None
        
    Returns:
        list: Отфильтрованные данные
    """
    if not table_data:
        return []
    
    if where_clause is None:
        return table_data
    
    column, value = next(iter(where_clause.items()))
    value_str = str(value)
    
    filtered_data = [
        record for record in table_data 
        if str(record.get(column)) == value_str
    ]
    
    return filtered_data


def update(table_data, set_clause, where_clause):
    """
    Обновляет записи в таблице.
    
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
    
    where_value_str = str(where_value)
    updated_count = 0
    
    for record in table_data:
        if str(record.get(where_column)) == where_value_str:
            record[set_column] = new_value
            updated_count += 1
    
    return table_data


def delete(table_data, where_clause):
    """
    Удаляет записи из таблицы.
    
    Args:
        table_data: Данные таблицы
        where_clause: Условие для поиска записей
        
    Returns:
        list: Обновленные данные таблицы
    """
    if not table_data or not where_clause:
        return table_data
    
    column, value = next(iter(where_clause.items()))
    value_str = str(value)
    
    filtered_data = [
        record for record in table_data 
        if str(record.get(column)) != value_str
    ]
    
    return filtered_data