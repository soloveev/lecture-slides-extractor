#!/usr/bin/env python3
"""
Lecture Slides Extractor - Главный модуль
Автоматическое извлечение слайдов из видео лекций и создание Markdown с транскриптом
"""

import argparse
import sys
import logging
from pathlib import Path

from .video_processor import VideoProcessor
from .transcript_parser import TranscriptParser
from .markdown_generator import MarkdownGenerator
from .config import (
    DEFAULT_SAMPLE_RATE,
    DEFAULT_THRESHOLD,
    DEFAULT_OUTPUT_FILE,
    DEFAULT_SLIDES_DIR,
    DEFAULT_CROP_REGION,
    CROP_REGION_BOTTOM_LEFT,
    CROP_REGION_BOTTOM_RIGHT,
    CROP_REGION_TOP_RIGHT,
    CROP_REGION_TOP_LEFT,
    CROP_REGION_CENTER
)


def setup_logging(verbose: bool = False):
    """Настройка логирования"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def choose_crop_region() -> str:
    """
    Интерактивный выбор области анализа кадра
    
    Returns:
        Выбранная область (bottom_left, bottom_right, top_right, top_left, center)
    """
    print("\n" + "=" * 80)
    print("ВЫБОР ОБЛАСТИ АНАЛИЗА")
    print("=" * 80)
    print("Выберите область кадра для анализа (где НЕТ лектора):")
    print()
    print("  1. Левый нижний угол (30%) - по умолчанию")
    print("  2. Правый нижний угол (30%)")
    print("  3. Правый верхний угол (30%)")
    print("  4. Левый верхний угол (30%)")
    print("  5. Центр (50%)")
    print()
    print("=" * 80)
    
    while True:
        try:
            choice = input("Ваш выбор (1-5, Enter для значения по умолчанию): ").strip()
            
            if not choice:  # Enter - значение по умолчанию
                print(f"✓ Выбрано: Левый нижний угол (по умолчанию)")
                return DEFAULT_CROP_REGION
            
            choice_num = int(choice)
            
            if choice_num == 1:
                print("✓ Выбрано: Левый нижний угол")
                return CROP_REGION_BOTTOM_LEFT
            elif choice_num == 2:
                print("✓ Выбрано: Правый нижний угол")
                return CROP_REGION_BOTTOM_RIGHT
            elif choice_num == 3:
                print("✓ Выбрано: Правый верхний угол")
                return CROP_REGION_TOP_RIGHT
            elif choice_num == 4:
                print("✓ Выбрано: Левый верхний угол")
                return CROP_REGION_TOP_LEFT
            elif choice_num == 5:
                print("✓ Выбрано: Центр")
                return CROP_REGION_CENTER
            else:
                print("⚠ Неверный выбор. Введите число от 1 до 5 или нажмите Enter.")
        except ValueError:
            print("⚠ Неверный ввод. Введите число от 1 до 5 или нажмите Enter.")
        except (EOFError, KeyboardInterrupt):
            print("\n✓ Используется значение по умолчанию: Левый нижний угол")
            return DEFAULT_CROP_REGION


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Lecture Slides Extractor - Извлечение слайдов из видео лекций',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --video lecture.mp4 --transcript transcript.txt
  %(prog)s --video lecture.mp4 --transcript transcript.txt --output result.md --threshold 0.9
  %(prog)s --video lecture.mp4 --transcript transcript.txt --sample-rate 2.0 --crop-region center

Автор: AI Lab
        """
    )
    
    # Обязательные параметры
    parser.add_argument(
        '--video',
        type=str,
        required=True,
        help='Путь к видеофайлу лекции (обязательный)'
    )
    
    parser.add_argument(
        '--transcript',
        type=str,
        required=True,
        help='Путь к файлу транскрипта с таймкодами (обязательный)'
    )
    
    # Опциональные параметры
    parser.add_argument(
        '--output',
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help=f'Путь к выходному Markdown файлу (по умолчанию: {DEFAULT_OUTPUT_FILE})'
    )
    
    parser.add_argument(
        '--slides-dir',
        type=str,
        default=DEFAULT_SLIDES_DIR,
        help=f'Папка для сохранения изображений слайдов (по умолчанию: {DEFAULT_SLIDES_DIR})'
    )
    
    parser.add_argument(
        '--sample-rate',
        type=float,
        default=DEFAULT_SAMPLE_RATE,
        help=f'Частота анализа кадров в секундах (по умолчанию: {DEFAULT_SAMPLE_RATE})'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f'Порог SSIM для детектирования смены слайдов 0-1 (по умолчанию: {DEFAULT_THRESHOLD})'
    )
    
    parser.add_argument(
        '--crop-region',
        type=str,
        choices=[CROP_REGION_BOTTOM_LEFT, CROP_REGION_BOTTOM_RIGHT, 
                 CROP_REGION_TOP_RIGHT, CROP_REGION_TOP_LEFT, CROP_REGION_CENTER],
        default=None,
        help=f'Область для анализа (bottom_left, bottom_right, top_right, top_left, center). '
             f'Если не указано, будет предложен интерактивный выбор.'
    )
    
    parser.add_argument(
        '--title',
        type=str,
        default='Лекция',
        help='Заголовок для Markdown документа (по умолчанию: Лекция)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод (debug mode)'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """Проверка корректности аргументов"""
    errors = []
    
    # Проверка существования файлов
    if not Path(args.video).exists():
        errors.append(f"Видеофайл не найден: {args.video}")
    
    if not Path(args.transcript).exists():
        errors.append(f"Файл транскрипта не найден: {args.transcript}")
    
    # Проверка диапазонов параметров
    if not 0.1 <= args.sample_rate <= 10:
        errors.append(f"sample-rate должен быть в диапазоне 0.1-10, получено: {args.sample_rate}")
    
    if not 0.5 <= args.threshold <= 1.0:
        errors.append(f"threshold должен быть в диапазоне 0.5-1.0, получено: {args.threshold}")
    
    return errors


def main():
    """Главная функция"""
    # Парсинг аргументов
    args = parse_arguments()
    
    # Настройка логирования
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Валидация аргументов
    errors = validate_arguments(args)
    if errors:
        logger.error("Ошибки в параметрах:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    try:
        logger.info("=" * 80)
        logger.info("LECTURE SLIDES EXTRACTOR")
        logger.info("=" * 80)
        logger.info(f"Видео: {args.video}")
        logger.info(f"Транскрипт: {args.transcript}")
        logger.info(f"Выходной файл: {args.output}")
        logger.info(f"Папка слайдов: {args.slides_dir}")
        logger.info("-" * 80)
        # Выбор области анализа (если не указана в аргументах)
        crop_region = args.crop_region
        if crop_region is None:
            crop_region = choose_crop_region()
        
        logger.info(f"Параметры обработки:")
        logger.info(f"  - Sample rate: {args.sample_rate}s")
        logger.info(f"  - Threshold: {args.threshold}")
        logger.info(f"  - Область анализа: {crop_region}")
        logger.info("=" * 80)
        
        # 1. Обработка видео
        logger.info("\n[ШАГ 1/3] ОБРАБОТКА ВИДЕО")
        video_processor = VideoProcessor(
            video_path=args.video,
            sample_rate=args.sample_rate,
            threshold=args.threshold,
            crop_region=crop_region
        )
        slides_data = video_processor.process(args.slides_dir)
        
        if not slides_data:
            logger.error("Не удалось извлечь ни одного слайда из видео!")
            sys.exit(1)
        
        logger.info(f"✓ Извлечено слайдов: {len(slides_data)}")
        
        # 2. Парсинг транскрипта
        logger.info("\n[ШАГ 2/3] ПАРСИНГ ТРАНСКРИПТА")
        transcript_parser = TranscriptParser()
        transcript_entries = transcript_parser.parse_transcript(args.transcript)
        
        if not transcript_entries:
            logger.warning("Транскрипт пуст или не удалось распарсить!")
        else:
            logger.info(f"✓ Распарсено сегментов транскрипта: {len(transcript_entries)}")
        
        # 3. Генерация Markdown
        logger.info("\n[ШАГ 3/3] ГЕНЕРАЦИЯ MARKDOWN")
        markdown_generator = MarkdownGenerator(transcript_parser)
        markdown_generator.generate_markdown(
            slides_data=slides_data,
            transcript_entries=transcript_entries,
            output_path=args.output,
            slides_dir=args.slides_dir,
            title=args.title
        )
        
        # Итоговая информация
        logger.info("\n" + "=" * 80)
        logger.info("✓ ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!")
        logger.info("=" * 80)
        logger.info(f"Результаты:")
        logger.info(f"  - Markdown документ: {args.output}")
        logger.info(f"  - Слайдов извлечено: {len(slides_data)}")
        logger.info(f"  - Папка со слайдами: {args.slides_dir}/")
        logger.info(f"  - Сегментов транскрипта: {len(transcript_entries)}")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.warning("\n\nОбработка прервана пользователем")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"\n\nОшибка при обработке: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()

