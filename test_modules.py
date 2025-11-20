#!/usr/bin/env python3
"""
Тестирование модулей Lecture Slides Extractor
"""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Тест импорта всех модулей"""
    print("Тестирование импорта модулей...")
    
    try:
        from src import config
        print("  ✓ config")
    except ImportError as e:
        print(f"  ✗ config: {e}")
        return False
    
    try:
        from src import transcript_parser
        print("  ✓ transcript_parser")
    except ImportError as e:
        print(f"  ✗ transcript_parser: {e}")
        return False
    
    try:
        from src import video_processor
        print("  ✓ video_processor")
    except ImportError as e:
        print(f"  ✗ video_processor: {e}")
        return False
    
    try:
        from src import markdown_generator
        print("  ✓ markdown_generator")
    except ImportError as e:
        print(f"  ✗ markdown_generator: {e}")
        return False
    
    try:
        from src import main
        print("  ✓ main")
    except ImportError as e:
        print(f"  ✗ main: {e}")
        return False
    
    return True


def test_transcript_parser():
    """Тест парсера транскриптов"""
    print("\nТестирование TranscriptParser...")
    
    from src.transcript_parser import TranscriptParser
    
    parser = TranscriptParser()
    
    # Тест парсинга времени
    tests = [
        ("0:02", 2),
        ("1:30", 90),
        ("1:23:45", 5025),
        ("12:05", 725),
    ]
    
    for time_str, expected in tests:
        result = parser.parse_timestamp(time_str)
        if result == expected:
            print(f"  ✓ parse_timestamp('{time_str}') = {result}")
        else:
            print(f"  ✗ parse_timestamp('{time_str}') = {result}, ожидалось {expected}")
            return False
    
    # Тест форматирования времени
    format_tests = [
        (2, "0:02"),
        (90, "1:30"),
        (5025, "1:23:45"),
    ]
    
    for seconds, expected in format_tests:
        result = parser.format_timestamp(seconds)
        if result == expected:
            print(f"  ✓ format_timestamp({seconds}) = '{result}'")
        else:
            print(f"  ✗ format_timestamp({seconds}) = '{result}', ожидалось '{expected}'")
            return False
    
    return True


def test_dependencies():
    """Тест зависимостей"""
    print("\nТестирование зависимостей...")
    
    deps = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('skimage', 'scikit-image'),
        ('PIL', 'Pillow'),
    ]
    
    all_ok = True
    for module, package in deps:
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - не установлен")
            all_ok = False
    
    return all_ok


def test_opencv_performance():
    """Тест производительности OpenCV на Apple Silicon"""
    print("\nТестирование OpenCV (Apple Silicon)...")
    
    try:
        import cv2
        import numpy as np
        import time
        
        # Создаём тестовое изображение
        img = np.random.randint(0, 255, (1920, 1080, 3), dtype=np.uint8)
        
        # Тест конвертации в grayscale
        start = time.time()
        for _ in range(100):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elapsed = time.time() - start
        
        print(f"  ✓ Конвертация BGR->Gray: {elapsed:.3f}s (100 итераций)")
        print(f"    Производительность: {100/elapsed:.1f} FPS")
        
        if elapsed < 1.0:
            print("  ✓ Производительность отличная (оптимизация работает)")
        elif elapsed < 2.0:
            print("  ⚠ Производительность приемлемая")
        else:
            print("  ⚠ Производительность низкая (возможно, Rosetta)")
        
        return True
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        return False


def check_architecture():
    """Проверка архитектуры процессора"""
    print("\nИнформация о системе...")
    
    import platform
    
    print(f"  Система: {platform.system()} {platform.release()}")
    print(f"  Архитектура: {platform.machine()}")
    print(f"  Python: {platform.python_version()}")
    
    if platform.machine() == 'arm64':
        print("  ✓ Apple Silicon (нативная архитектура)")
    elif platform.machine() == 'x86_64':
        print("  ⚠ Intel/Rosetta (возможна медленная работа)")
    else:
        print(f"  ? Неизвестная архитектура: {platform.machine()}")


def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("LECTURE SLIDES EXTRACTOR - ТЕСТИРОВАНИЕ")
    print("=" * 60)
    
    check_architecture()
    
    if not test_dependencies():
        print("\n❌ Не все зависимости установлены!")
        print("Выполните: pip install -r requirements.txt")
        return False
    
    if not test_imports():
        print("\n❌ Ошибка импорта модулей!")
        return False
    
    if not test_transcript_parser():
        print("\n❌ Ошибка в TranscriptParser!")
        return False
    
    if not test_opencv_performance():
        print("\n⚠ Предупреждение о производительности OpenCV")
    
    print("\n" + "=" * 60)
    print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)
    print("\nПриложение готово к использованию.")
    print("Для запуска используйте:")
    print("  python3 src/main.py --video <файл> --transcript <файл>")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

