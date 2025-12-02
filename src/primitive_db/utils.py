#!/usr/bin/env python3
"""
Вспомогательные функции для работы с файлами.
"""

import json
import os

from .constants import (
    DATA_DIR,
    DEFAULT_ENCODING,
    META_FILE,
)


def load_metadata(filepath=META_FILE):
    """
    Загружает метаданные из JSON-файла.
    
    Args:
        filepath: Путь к файлу с метаданными
        
    Returns:
        dict: Загруженные метаданные или пустой словарь
    """
    try:
        with open(filepath, 'r', encoding=DEFAULT_ENCODING) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(data, filepath=META_FILE):
    """
    Сохраняет метаданные в JSON-файл.
    
    Args:
        data: Данные для сохранения
        filepath: Путь к файлу для сохранения
    """
    with open(filepath, 'w', encoding=DEFAULT_ENCODING) as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_table_data(table_name, data_dir=DATA_DIR):
    """
    Загружает данные таблицы из JSON-файла.
    
    Args:
        table_name: Имя таблицы
        data_dir: Директория с данными
        
    Returns:
        list: Данные таблицы или пустой список
    """
    # Создаем директорию если не существует
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, f"{table_name}.json")
    try:
        with open(filepath, 'r', encoding=DEFAULT_ENCODING) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data, data_dir=DATA_DIR):
    """
    Сохраняет данные таблицы в JSON-файл.
    
    Args:
        table_name: Имя таблицы
        data: Данные для сохранения
        data_dir: Директория с данными
    """
    # Создаем директорию если не существует
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, f"{table_name}.json")
    with open(filepath, 'w', encoding=DEFAULT_ENCODING) as f:
        json.dump(data, f, indent=2, ensure_ascii=False)