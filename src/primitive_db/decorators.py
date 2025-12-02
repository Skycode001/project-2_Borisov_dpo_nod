#!/usr/bin/env python3
"""
Декораторы для обработки ошибок, логирования и подтверждения действий.
"""

import time

from .constants import (
    CANCELLATION_MESSAGE,
    CONFIRMATION_PROMPT_TEMPLATE,
    FILE_NOT_FOUND_MESSAGE,
    KEY_ERROR_MESSAGE,
    TIME_FORMAT_TEMPLATE,
    UNEXPECTED_ERROR_MESSAGE,
    VALIDATION_ERROR_MESSAGE,
)


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок базы данных.
    
    Перехватывает:
    - FileNotFoundError: файл данных не найден
    - KeyError: таблица или столбец не найден
    - ValueError: ошибки валидации типов
    - Exception: все остальные ошибки
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(FILE_NOT_FOUND_MESSAGE)
            return None
        except KeyError as e:
            print(KEY_ERROR_MESSAGE.format(e))
            return None
        except ValueError as e:
            print(VALIDATION_ERROR_MESSAGE.format(e))
            return None
        except Exception as e:
            print(UNEXPECTED_ERROR_MESSAGE.format(e))
            return None
    # Сохраняем имя и документацию оригинальной функции
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            prompt_msg = CONFIRMATION_PROMPT_TEMPLATE.format(action_name)
            response = input(prompt_msg).strip().lower()
            
            if response != 'y':
                print(CANCELLATION_MESSAGE)
                if args:
                    return args[0]  # ← возвращаем первый аргумент
                return None
            
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


def log_time(func):
    """
    Декоратор для измерения времени выполнения функции.
    """
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        
        elapsed = end_time - start_time
        print(TIME_FORMAT_TEMPLATE.format(func.__name__, elapsed))
        
        return result
    # Сохраняем имя и документацию
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def create_cacher():
    """
    Фабрика функций для кэширования результатов.
    
    Returns:
        Функция cache_result для кэширования
    """
    cache = {}
    
    def cache_result(key, value_func):
        """
        Кэширует результаты выполнения функций.
        
        Args:
            key: Ключ для кэша
            value_func: Функция для получения значения
            
        Returns:
            Результат выполнения value_func (из кэша или новый)
        """
        if key in cache:
            return cache[key]
        
        result = value_func()
        cache[key] = result
        return result
    
    return cache_result