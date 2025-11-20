#!/usr/bin/env python3
"""
Обработка видео из указанной папки
Находит видео и транскрипт в папке и обрабатывает их
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.video_processor import VideoProcessor
from src.transcript_parser import TranscriptParser
from src.markdown_generator import MarkdownGenerator
from src.config import (
    DEFAULT_SAMPLE_RATE, 
    DEFAULT_THRESHOLD, 
    DEFAULT_CROP_REGION,
    CROP_REGION_BOTTOM_LEFT,
    CROP_REGION_BOTTOM_RIGHT,
    CROP_REGION_TOP_RIGHT,
    CROP_REGION_TOP_LEFT,
    CROP_REGION_CENTER
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


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


class FolderProcessor:
    """Обработчик видео из указанной папки"""
    
    VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.m4v']
    TRANSCRIPT_EXTENSIONS = ['.txt']
    
    def __init__(
        self,
        sample_rate: float = DEFAULT_SAMPLE_RATE,
        threshold: float = DEFAULT_THRESHOLD,
        crop_region: str = DEFAULT_CROP_REGION,
        force: bool = False
    ):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.crop_region = crop_region
        self.force = force
    
    def find_video_file(self, folder: Path) -> Path:
        """Находит видеофайл в папке"""
        for ext in self.VIDEO_EXTENSIONS:
            videos = list(folder.glob(f'*{ext}'))
            if videos:
                return videos[0]  # Берём первый найденный
        return None
    
    def find_transcript_file(self, folder: Path) -> Path:
        """Находит файл транскрипта в папке"""
        for ext in self.TRANSCRIPT_EXTENSIONS:
            transcripts = list(folder.glob(f'*{ext}'))
            if transcripts:
                return transcripts[0]  # Берём первый найденный
        return None
    
    def process_folder(self, folder: Path) -> bool:
        """
        Обрабатывает одну папку с видео и транскриптом
        
        Args:
            folder: Путь к папке
        
        Returns:
            True если успешно, False если ошибка
        """
        logger.info("=" * 80)
        logger.info(f"Обработка папки: {folder.name}")
        logger.info("=" * 80)
        
        # Ищем видео
        video_file = self.find_video_file(folder)
        if not video_file:
            logger.warning(f"Видеофайл не найден в {folder.name}")
            return False
        
        logger.info(f"✓ Найдено видео: {video_file.name}")
        
        # Ищем транскрипт
        transcript_file = self.find_transcript_file(folder)
        if not transcript_file:
            logger.warning(f"Транскрипт не найден в {folder.name}")
            return False
        
        logger.info(f"✓ Найден транскрипт: {transcript_file.name}")
        
        # Определяем имена выходных файлов (по имени видео)
        video_basename = video_file.stem  # Имя без расширения
        output_md = folder / f"{video_basename}.md"
        slides_dir = folder / f"{video_basename}_slides"
        
        # Проверяем, не обработано ли уже
        if output_md.exists():
            if self.force:
                logger.info(f"⚠ Файл {output_md.name} уже существует - автоматическая перезапись")
            else:
                logger.info(f"⚠ Файл {output_md.name} уже существует")
                response = input("  Перезаписать? (y/n): ").lower()
                if response != 'y':
                    logger.info("  Пропускаем...")
                    return False
        
        try:
            # 1. Обработка видео
            logger.info(f"\n[1/3] Обработка видео...")
            video_processor = VideoProcessor(
                video_path=str(video_file),
                sample_rate=self.sample_rate,
                threshold=self.threshold,
                crop_region=self.crop_region
            )
            slides_data = video_processor.process(str(slides_dir))
            
            if not slides_data:
                logger.error("Не удалось извлечь слайды!")
                return False
            
            logger.info(f"✓ Извлечено слайдов: {len(slides_data)}")
            
            # 2. Парсинг транскрипта
            logger.info(f"\n[2/3] Парсинг транскрипта...")
            transcript_parser = TranscriptParser()
            transcript_entries = transcript_parser.parse_transcript(str(transcript_file))
            
            logger.info(f"✓ Распарсено сегментов: {len(transcript_entries)}")
            
            # 3. Генерация Markdown
            logger.info(f"\n[3/3] Генерация Markdown...")
            markdown_generator = MarkdownGenerator(transcript_parser)
            
            # Используем имя папки как заголовок
            title = folder.name.replace('-', ' ').replace('_', ' ').title()
            
            markdown_generator.generate_markdown(
                slides_data=slides_data,
                transcript_entries=transcript_entries,
                output_path=str(output_md),
                slides_dir=slides_dir.name,  # Относительное имя папки
                title=title
            )
            
            logger.info("\n" + "=" * 80)
            logger.info(f"✓ УСПЕШНО ОБРАБОТАНО: {folder.name}")
            logger.info("=" * 80)
            logger.info(f"Результаты:")
            logger.info(f"  📄 Markdown: {output_md.name}")
            logger.info(f"  🖼️  Слайды: {slides_dir.name}/ ({len(slides_data)} файлов)")
            logger.info("=" * 80 + "\n")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке {folder.name}: {e}")
            return False
    


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Обработка видео из указанной папки',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Пример использования:
  python3 auto_process.py material/one-one-decomposition

Структура папки:
  material/one-one-decomposition/
    ├── video.mp4
    └── transcript.txt

Результат:
  material/one-one-decomposition/
    ├── video.mp4
    ├── transcript.txt
    ├── video.md              ← Сгенерированный Markdown
    └── video_slides/         ← Папка со слайдами
        ├── slide_001.png
        └── slide_002.png
        """
    )
    
    parser.add_argument(
        'folder',
        type=str,
        help='Путь к папке с видео и транскриптом'
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
        help=f'Порог SSIM для детектирования смены слайдов (по умолчанию: {DEFAULT_THRESHOLD})'
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
        '--force',
        action='store_true',
        help='Автоматически перезаписывать существующие файлы без подтверждения'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование папки
    folder_path = Path(args.folder)
    if not folder_path.exists():
        logger.error(f"Папка не найдена: {folder_path}")
        sys.exit(1)
    
    if not folder_path.is_dir():
        logger.error(f"Это не папка: {folder_path}")
        sys.exit(1)
    
    # Выбор области анализа (если не указана в аргументах)
    crop_region = args.crop_region
    if crop_region is None:
        crop_region = choose_crop_region()
    
    # Создаём процессор
    processor = FolderProcessor(
        sample_rate=args.sample_rate,
        threshold=args.threshold,
        crop_region=crop_region,
        force=args.force
    )
    
    try:
        success = processor.process_folder(folder_path)
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.warning("\n\nОбработка прервана пользователем")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"\n\nКритическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

