"""
Модуль для парсинга транскрипта лекции с таймкодами
"""

import re
from typing import List, Tuple, Optional


class TranscriptEntry:
    """Класс для хранения одного сегмента транскрипта"""
    
    def __init__(self, start_time: float, end_time: float, text: str):
        self.start_time = start_time  # в секундах
        self.end_time = end_time      # в секундах
        self.text = text.strip()
    
    def __repr__(self):
        return f"TranscriptEntry({self.start_time}s - {self.end_time}s: {self.text[:50]}...)"


class TranscriptParser:
    """Парсер транскриптов с таймкодами"""
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> float:
        """
        Конвертирует строку времени в секунды
        Поддерживает форматы: (MM:SS), (H:MM:SS), (HH:MM:SS)
        
        Args:
            timestamp_str: Строка вида "0:02" или "1:23:45"
        
        Returns:
            Время в секундах
        """
        # Убираем лишние символы
        timestamp_str = timestamp_str.strip().strip('()')
        
        parts = timestamp_str.split(':')
        
        if len(parts) == 2:  # MM:SS
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:  # H:MM:SS или HH:MM:SS
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        else:
            raise ValueError(f"Неверный формат времени: {timestamp_str}")
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """
        Конвертирует секунды в читаемый формат времени
        
        Args:
            seconds: Время в секундах
        
        Returns:
            Строка вида "H:MM:SS" или "MM:SS"
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def parse_transcript(self, file_path: str) -> List[TranscriptEntry]:
        """
        Парсит файл транскрипта
        
        Формат файла:
        |(MM:SS - MM:SS)
        |Текст сегмента
        |
        
        Args:
            file_path: Путь к файлу транскрипта
        
        Returns:
            Список TranscriptEntry
        """
        entries = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Паттерн для поиска временных меток: |(MM:SS - MM:SS)
        pattern = r'\|?\((\d+:\d+(?::\d+)?)\s*-\s*(\d+:\d+(?::\d+)?)\)'
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Ищем строку с таймкодом
            match = re.search(pattern, line)
            if match:
                start_str = match.group(1)
                end_str = match.group(2)
                
                start_time = self.parse_timestamp(start_str)
                end_time = self.parse_timestamp(end_str)
                
                # Следующая строка должна содержать текст
                i += 1
                text_lines = []
                
                while i < len(lines):
                    text_line = lines[i].strip()
                    # Если строка начинается с |, убираем этот символ
                    if text_line.startswith('|'):
                        text_line = text_line[1:].strip()
                    
                    # Если новый таймкод - заканчиваем сбор текста
                    if re.search(pattern, text_line):
                        break
                    
                    # Пропускаем пустые строки, но продолжаем собирать текст
                    # (пустые строки могут быть внутри сегмента)
                    if text_line:
                        text_lines.append(text_line)
                    
                    i += 1
                
                if text_lines:
                    text = ' '.join(text_lines)
                    entries.append(TranscriptEntry(start_time, end_time, text))
            else:
                i += 1
        
        return entries
    
    @staticmethod
    def _split_text_proportionally(text: str, start_time: float, end_time: float, 
                                   slide_times: List[float]) -> List[Tuple[float, str]]:
        """
        Разбивает текст пропорционально времени между слайдами
        
        Args:
            text: Текст для разбиения
            start_time: Начало интервала текста
            end_time: Конец интервала текста
            slide_times: Список времен слайдов внутри интервала (отсортированный)
        
        Returns:
            Список кортежей (время_слайда, часть_текста)
        """
        if not slide_times:
            return []
        
        # Если один слайд - весь текст к нему
        if len(slide_times) == 1:
            return [(slide_times[0], text)]
        
        # Разбиваем текст на предложения (сохраняя разделители)
        # Используем более умное разбиение: точка/восклицательный/вопросительный + пробел
        sentences = re.split(r'([.!?]+(?:\s+|$))', text)
        # Объединяем предложения с их разделителями
        sentences_combined = []
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentences_combined.append(sentences[i] + sentences[i + 1])
            elif sentences[i].strip():
                sentences_combined.append(sentences[i])
        
        if not sentences_combined:
            sentences_combined = [text]
        
        # Вычисляем границы временных отрезков для каждого слайда
        text_duration = end_time - start_time
        num_slides = len(slide_times)
        
        # Определяем границы для каждого слайда (середина между слайдами)
        boundaries = []
        for i in range(num_slides):
            if i == 0:
                # Первый слайд: от начала до середины между первым и вторым слайдом
                boundary_end = (slide_times[0] + slide_times[1]) / 2
                boundaries.append((start_time, boundary_end))
            elif i == num_slides - 1:
                # Последний слайд: от середины между предпоследним и последним до конца
                boundary_start = (slide_times[i - 1] + slide_times[i]) / 2
                boundaries.append((boundary_start, end_time))
            else:
                # Средние слайды: от середины между предыдущим и текущим до середины между текущим и следующим
                boundary_start = (slide_times[i - 1] + slide_times[i]) / 2
                boundary_end = (slide_times[i] + slide_times[i + 1]) / 2
                boundaries.append((boundary_start, boundary_end))
        
        # Распределяем предложения пропорционально времени
        result = []
        sentence_idx = 0
        total_sentences = len(sentences_combined)
        
        for i, (slide_time, (boundary_start, boundary_end)) in enumerate(zip(slide_times, boundaries)):
            segment_duration = boundary_end - boundary_start
            segment_ratio = segment_duration / text_duration if text_duration > 0 else 1.0 / num_slides
            
            # Количество предложений для этого слайда (пропорционально времени)
            num_sentences_for_slide = max(1, round(total_sentences * segment_ratio))
            
            # Берем предложения для этого слайда
            end_idx = min(sentence_idx + num_sentences_for_slide, total_sentences)
            slide_sentences = sentences_combined[sentence_idx:end_idx]
            sentence_idx = end_idx
            
            if slide_sentences:
                slide_text = ''.join(slide_sentences).strip()
                if slide_text:
                    result.append((slide_time, slide_text))
        
        # Если остались предложения (из-за округления), добавляем их к последнему слайду
        if sentence_idx < total_sentences and result:
            remaining = ''.join(sentences_combined[sentence_idx:]).strip()
            if remaining:
                last_slide_time, last_text = result[-1]
                result[-1] = (last_slide_time, last_text + ' ' + remaining)
        
        return result
    
    def distribute_text_proportionally(
        self,
        slides_data: List[Tuple[str, float]],
        transcript_entries: List[TranscriptEntry]
    ) -> dict:
        """
        Распределяет текст из транскрипта пропорционально между слайдами
        
        Args:
            slides_data: Список кортежей (путь_к_слайду, timestamp)
            transcript_entries: Список всех записей транскрипта
        
        Returns:
            Словарь {timestamp_слайда: текст}
        """
        # Создаем словарь для хранения текста каждого слайда
        slide_texts = {timestamp: [] for _, timestamp in slides_data}
        
        # Для каждого сегмента транскрипта
        for entry in transcript_entries:
            text_start = entry.start_time
            text_end = entry.end_time
            
            # Находим все слайды, которые попадают в интервал этого текста
            slides_in_interval = []
            for i, (_, slide_time) in enumerate(slides_data):
                next_slide_time = slides_data[i + 1][1] if i + 1 < len(slides_data) else float('inf')
                
                # Проверяем пересечение интервалов:
                # Текст: [text_start, text_end]
                # Слайд: [slide_time, next_slide_time]
                has_intersection = (
                    (text_start <= slide_time < text_end) or  # Начало слайда в интервале текста
                    (text_start < next_slide_time <= text_end) or  # Конец слайда в интервале текста
                    (slide_time <= text_start and text_end <= next_slide_time) or  # Текст полностью внутри слайда
                    (text_start <= slide_time and text_end >= next_slide_time)  # Текст полностью покрывает слайд
                )
                
                if has_intersection:
                    slides_in_interval.append(slide_time)
            
            # Если слайдов нет - пропускаем
            if not slides_in_interval:
                continue
            
            # Сортируем слайды по времени
            slides_in_interval.sort()
            
            # Если один слайд - весь текст к нему
            if len(slides_in_interval) == 1:
                slide_texts[slides_in_interval[0]].append(entry.text)
            else:
                # Несколько слайдов - распределяем пропорционально
                distributed = self._split_text_proportionally(
                    entry.text, text_start, text_end, slides_in_interval
                )
                for slide_time, text_part in distributed:
                    if text_part:
                        slide_texts[slide_time].append(text_part)
        
        # Объединяем текст для каждого слайда
        result = {}
        for slide_time, texts in slide_texts.items():
            if texts:
                result[slide_time] = '\n\n'.join(texts)
            else:
                result[slide_time] = ""
        
        return result
    
    def find_text_for_slide(
        self,
        slide_time: float,
        next_slide_time: Optional[float],
        transcript_entries: List[TranscriptEntry]
    ) -> str:
        """
        Находит весь текст, который пересекается с интервалом слайда
        (УСТАРЕВШИЙ метод - используется для обратной совместимости)
        
        Args:
            slide_time: Время появления текущего слайда (в секундах)
            next_slide_time: Время появления следующего слайда (в секундах) или None
            transcript_entries: Список всех записей транскрипта
        
        Returns:
            Объединенный текст для этого слайда
        """
        texts = []
        
        # Определяем интервал слайда
        slide_end_time = next_slide_time if next_slide_time is not None else float('inf')
        
        for entry in transcript_entries:
            text_start = entry.start_time
            text_end = entry.end_time
            
            # Проверяем пересечение интервалов
            has_intersection = (
                (slide_time <= text_start < slide_end_time) or
                (slide_time < text_end <= slide_end_time) or
                (text_start <= slide_time and text_end >= slide_end_time)
            )
            
            if has_intersection:
                texts.append(entry.text)
        
        return '\n\n'.join(texts) if texts else ""


if __name__ == "__main__":
    # Тест парсера
    parser = TranscriptParser()
    
    # Тест парсинга времени
    assert parser.parse_timestamp("0:02") == 2
    assert parser.parse_timestamp("1:30") == 90
    assert parser.parse_timestamp("1:23:45") == 5025
    
    # Тест форматирования времени
    assert parser.format_timestamp(2) == "0:02"
    assert parser.format_timestamp(90) == "1:30"
    assert parser.format_timestamp(5025) == "1:23:45"
    
    print("✓ Все тесты TranscriptParser прошли успешно!")

