"""
Модуль для генерации Markdown документа с слайдами и транскриптом
"""

from pathlib import Path
from typing import List, Tuple
import logging

from .transcript_parser import TranscriptParser

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """Генератор Markdown документов"""
    
    def __init__(self, transcript_parser: TranscriptParser):
        """
        Args:
            transcript_parser: Экземпляр TranscriptParser
        """
        self.parser = transcript_parser
    
    def format_slide_section(
        self,
        slide_num: int,
        slide_path: str,
        timestamp: float,
        text: str,
        slides_dir: str
    ) -> str:
        """
        Форматирует секцию одного слайда
        
        Args:
            slide_num: Номер слайда
            slide_path: Путь к изображению слайда
            timestamp: Время появления слайда
            text: Текст транскрипта для этого слайда
            slides_dir: Название папки со слайдами
        
        Returns:
            Отформатированная секция Markdown
        """
        time_str = self.parser.format_timestamp(timestamp)
        filename = Path(slide_path).name
        
        section = f"## Слайд {slide_num} ({time_str})\n\n"
        # Используем угловые скобки для путей с пробелами
        section += f"![Слайд {slide_num}](<./{slides_dir}/{filename}>)\n\n"
        
        if text:
            section += f"{text}\n"
        else:
            section += "_[Текст для этого слайда не найден в транскрипте]_\n"
        
        return section
    
    def generate_markdown(
        self,
        slides_data: List[Tuple[str, float]],
        transcript_entries,
        output_path: str,
        slides_dir: str = "slides",
        title: str = "Лекция"
    ) -> None:
        """
        Генерирует полный Markdown документ
        
        Args:
            slides_data: Список кортежей (путь_к_слайду, timestamp)
            transcript_entries: Список TranscriptEntry из парсера
            output_path: Путь к выходному MD файлу
            slides_dir: Название папки со слайдами
            title: Заголовок документа
        """
        logger.info(f"Генерация Markdown документа: {output_path}")
        
        # Начало документа
        markdown = f"# {title}\n\n"
        markdown += f"_Автоматически сгенерировано с помощью Lecture Slides Extractor_\n\n"
        markdown += f"**Всего слайдов:** {len(slides_data)}\n\n"
        markdown += "---\n\n"
        
        # Распределяем текст пропорционально между слайдами (без дублирования)
        distributed_texts = self.parser.distribute_text_proportionally(
            slides_data, transcript_entries
        )
        
        # Генерируем секцию для каждого слайда
        for i, (slide_path, timestamp) in enumerate(slides_data, start=1):
            # Получаем текст для этого слайда из распределенного словаря
            text = distributed_texts.get(timestamp, "")
            
            # Форматируем секцию
            section = self.format_slide_section(
                i, slide_path, timestamp, text, slides_dir
            )
            markdown += section
            
            # Разделитель между слайдами (кроме последнего)
            if i < len(slides_data):
                markdown += "\n---\n\n"
            
            logger.info(f"Добавлен слайд {i}/{len(slides_data)} ({len(text)} символов текста)")
        
        # Сохраняем файл
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        logger.info(f"✓ Markdown документ сохранён: {output_path}")
        logger.info(f"  Размер файла: {len(markdown)} символов")


if __name__ == "__main__":
    print("MarkdownGenerator модуль загружен успешно!")

