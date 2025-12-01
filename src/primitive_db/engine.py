#!/usr/bin/env python3
"""
Модуль engine - ядро приложения, отвечает за запуск и игровой цикл
"""

def welcome():
    """
    Функция приветствия и запуска игрового цикла
    """
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    
    while True:
        command = input("Введите команду: ").strip().lower()
        
        if command == "exit":
            print("Выход из программы...")
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print(f"Неизвестная команда: {command}")
            print("Доступные команды: exit, help")


def main():
    """Основная функция запуска приложения"""
    print("Первая попытка запустить проект!")
    welcome()


if __name__ == "__main__":
    main()