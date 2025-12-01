#!/usr/bin/env python3
"""
Парсеры для сложных команд SQL-like.
"""

import shlex


def parse_where_clause(where_str):
    """
    Парсит WHERE условие в формате "столбец = значение".
    
    Args:
        where_str: Строка условия
        
    Returns:
        dict: {'column': value} или None если условие пустое
    """
    if not where_str or not where_str.strip():
        return None
    
    where_str = where_str.strip()
    if where_str.startswith('(') and where_str.endswith(')'):
        where_str = where_str[1:-1].strip()
    
    try:
        parts = where_str.split('=', 1)
        if len(parts) != 2:
            return None
        
        column = parts[0].strip()
        value_str = parts[1].strip()
        
        # Обрабатываем значения
        value = parse_value(value_str)
        
        return {column: value}
    except Exception:
        return None


def parse_set_clause(set_str):
    """
    Парсит SET условие в формате "столбец = новое_значение".
    
    Args:
        set_str: Строка условия
        
    Returns:
        dict: {'column': 'new_value'}
    """
    if not set_str or not set_str.strip():
        return {}
    
    try:
        set_str = set_str.lower().replace('set', '', 1).strip()
        parts = set_str.split('=', 1)
        
        if len(parts) != 2:
            return {}
        
        column = parts[0].strip()
        value_str = parts[1].strip()
        value = parse_value(value_str)
        
        return {column: value}
    except Exception:
        return {}


def parse_values(values_str):
    """
    Парсит значения для INSERT в формате "(значение1, значение2, ...)".
    
    Args:
        values_str: Строка со значениями
        
    Returns:
        list: Список значений
    """
    if not values_str or not values_str.strip():
        return []
    
    try:
        values_str = values_str.lower().replace('values', '', 1).strip()
        if values_str.startswith('(') and values_str.endswith(')'):
            values_str = values_str[1:-1].strip()
        
        parts = shlex.split(values_str.replace(',', ' '))
        values = []
        
        for part in parts:
            if part == ',' or not part:
                continue
            values.append(parse_value(part))
        
        return values
    except Exception:
        return []


def parse_value(value_str):
    """
    Парсит одиночное значение, преобразуя к правильному типу.
    
    Args:
        value_str: Строка со значением
        
    Returns:
        Значение правильного типа
    """
    # Убираем кавычки
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # Булевы значения
    if value_str.lower() == 'true':
        return True
    elif value_str.lower() == 'false':
        return False
    
    # Числа
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        return value_str  # Оставляем как строку