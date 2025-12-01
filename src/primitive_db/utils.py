#!/usr/bin/env python3
"""
Вспомогательные функции для работы с файлами.
"""

import json


def load_metadata(filepath="db_meta.json"):
    """
    Загружает метаданные из JSON-файла.
    
    Args:
        filepath: Путь к файлу с метаданными
        
    Returns:
        dict: Загруженные метаданные или пустой словарь
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(data, filepath="db_meta.json"):
    """
    Сохраняет метаданные в JSON-файл.
    
    Args:
        data: Данные для сохранения
        filepath: Путь к файлу для сохранения
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)