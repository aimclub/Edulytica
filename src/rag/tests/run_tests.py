#!/usr/bin/env python3
"""
Скрипт для запуска всех модульных тестов RAG модуля
"""
import unittest
import sys
import os

# Добавляем родительскую директорию в путь для правильного импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем все тесты
loader = unittest.TestLoader()
start_dir = os.path.dirname(os.path.abspath(__file__))
suite = loader.discover(start_dir, pattern="test_*.py")

# Запускаем тесты
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Выходим с кодом ошибки, если были неудачные тесты
sys.exit(not result.wasSuccessful()) 