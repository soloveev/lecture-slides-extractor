"""
Модуль для обработки видео и извлечения слайдов
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from skimage.metrics import structural_similarity as ssim
import logging

from .config import (
    MIN_SLIDE_DURATION,
    CROP_REGION_BOTTOM_LEFT,
    CROP_REGION_BOTTOM_RIGHT,
    CROP_REGION_TOP_RIGHT,
    CROP_REGION_TOP_LEFT,
    CROP_REGION_CENTER,
    DEFAULT_CROP_REGION,
    CROP_SIZE_CORNER,
    CROP_SIZE_CENTER
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Slide:
    """Класс для хранения информации о слайде"""
    
    def __init__(self, frame: np.ndarray, timestamp: float, frame_number: int):
        self.frame = frame           # Изображение кадра
        self.timestamp = timestamp   # Время в секундах
        self.frame_number = frame_number
    
    def __repr__(self):
        return f"Slide(time={self.timestamp:.2f}s, frame={self.frame_number})"


class VideoProcessor:
    """Обработчик видео для извлечения слайдов"""
    
    def __init__(
        self,
        video_path: str,
        sample_rate: float = 1.0,
        threshold: float = 0.85,
        crop_region: str = DEFAULT_CROP_REGION
    ):
        """
        Args:
            video_path: Путь к видеофайлу
            sample_rate: Частота анализа кадров (секунды между кадрами)
            threshold: Порог SSIM для детектирования смены (0-1)
            crop_region: Область для анализа ('bottom_left', 'bottom_right', 'top_right', 'top_left', 'center')
        """
        self.video_path = video_path
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.crop_region = crop_region
        
        # Откроем видео для получения метаданных
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Не удалось открыть видеофайл: {video_path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        logger.info(f"Видео загружено: {video_path}")
        logger.info(f"FPS: {self.fps}, Всего кадров: {self.total_frames}, Длительность: {self.duration:.2f}s")
    
    def __del__(self):
        """Закрываем видео при удалении объекта"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
    
    def _crop_frame_region(self, frame: np.ndarray) -> np.ndarray:
        """
        Вырезает область кадра для анализа в зависимости от выбранной области
        
        Args:
            frame: Исходный кадр
        
        Returns:
            Обрезанный кадр для анализа
        """
        height, width = frame.shape[:2]
        
        if self.crop_region == CROP_REGION_BOTTOM_LEFT:
            # Левый нижний угол: 30% ширины, 30% высоты
            crop_width = int(width * CROP_SIZE_CORNER)
            crop_height = int(height * CROP_SIZE_CORNER)
            x_start = 0
            y_start = height - crop_height
            
        elif self.crop_region == CROP_REGION_BOTTOM_RIGHT:
            # Правый нижний угол: 30% ширины, 30% высоты
            crop_width = int(width * CROP_SIZE_CORNER)
            crop_height = int(height * CROP_SIZE_CORNER)
            x_start = width - crop_width
            y_start = height - crop_height
            
        elif self.crop_region == CROP_REGION_TOP_RIGHT:
            # Правый верхний угол: 30% ширины, 30% высоты
            crop_width = int(width * CROP_SIZE_CORNER)
            crop_height = int(height * CROP_SIZE_CORNER)
            x_start = width - crop_width
            y_start = 0
            
        elif self.crop_region == CROP_REGION_TOP_LEFT:
            # Левый верхний угол: 30% ширины, 30% высоты
            crop_width = int(width * CROP_SIZE_CORNER)
            crop_height = int(height * CROP_SIZE_CORNER)
            x_start = 0
            y_start = 0
            
        elif self.crop_region == CROP_REGION_CENTER:
            # Центр: 50% ширины, 50% высоты (чтобы лектор не попал)
            crop_width = int(width * CROP_SIZE_CENTER)
            crop_height = int(height * CROP_SIZE_CENTER)
            x_start = (width - crop_width) // 2
            y_start = (height - crop_height) // 2
            
        else:
            # По умолчанию левый нижний угол
            crop_width = int(width * CROP_SIZE_CORNER)
            crop_height = int(height * CROP_SIZE_CORNER)
            x_start = 0
            y_start = height - crop_height
        
        return frame[y_start:y_start+crop_height, x_start:x_start+crop_width]
    
    def get_region_description(self) -> str:
        """Возвращает описание выбранной области для логирования"""
        descriptions = {
            CROP_REGION_BOTTOM_LEFT: "левый нижний угол (30%)",
            CROP_REGION_BOTTOM_RIGHT: "правый нижний угол (30%)",
            CROP_REGION_TOP_RIGHT: "правый верхний угол (30%)",
            CROP_REGION_TOP_LEFT: "левый верхний угол (30%)",
            CROP_REGION_CENTER: "центр (50%)"
        }
        return descriptions.get(self.crop_region, "неизвестная область")
    
    def compare_frames(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Сравнивает два кадра с помощью комбинации метрик
        
        Args:
            frame1: Первый кадр
            frame2: Второй кадр
        
        Returns:
            Коэффициент сходства (0-1, где 1 - идентичные)
        """
        # Конвертируем в grayscale для более быстрого сравнения
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Приводим к одному размеру на случай разных размеров
        if gray1.shape != gray2.shape:
            gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
        
        # Применяем размытие для уменьшения влияния шума/сжатия/антиалиасинга
        gray1_blur = cv2.GaussianBlur(gray1, (5, 5), 0)
        gray2_blur = cv2.GaussianBlur(gray2, (5, 5), 0)
        
        # Метрика 1: SSIM с правильным data_range
        ssim_value, _ = ssim(gray1_blur, gray2_blur, full=True, data_range=255)
        
        # Метрика 2: Процент пикселей, которые отличаются меньше чем на 3 единицы
        # Это более мягкая метрика, которая игнорирует мелкие различия
        diff = np.abs(gray1_blur.astype(np.float32) - gray2_blur.astype(np.float32))
        similar_pixels = np.sum(diff < 3.0)  # Пиксели с разницей < 3
        total_pixels = gray1_blur.size
        pixel_similarity = similar_pixels / total_pixels
        
        # Комбинируем метрики: берем максимум из SSIM и pixel_similarity
        # Это позволяет учитывать как структурное сходство, так и процент совпадающих пикселей
        similarity = max(ssim_value, pixel_similarity)
        
        return similarity
    
    def extract_frames(self) -> List[Tuple[np.ndarray, float, int]]:
        """
        Извлекает кадры из видео с заданной частотой
        
        Returns:
            Список кортежей (ПОЛНЫЙ_кадр, время, номер_кадра)
        """
        frames = []
        frame_interval = int(self.fps * self.sample_rate)
        
        logger.info(f"Извлечение кадров с интервалом {self.sample_rate}s (каждый {frame_interval} кадр)")
        
        frame_number = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Берём кадры с заданным интервалом
            if frame_number % frame_interval == 0:
                timestamp = frame_number / self.fps
                # Сохраняем ПОЛНЫЙ кадр (обрезку делаем только для анализа)
                frames.append((frame.copy(), timestamp, frame_number))
                
                if len(frames) % 100 == 0:
                    logger.info(f"Обработано кадров: {len(frames)} (время: {timestamp:.1f}s)")
            
            frame_number += 1
        
        logger.info(f"Всего извлечено кадров: {len(frames)}")
        return frames
    
    def detect_slide_changes(self, frames: List[Tuple[np.ndarray, float, int]]) -> List[Slide]:
        """
        Обнаруживает смену слайдов путём сравнения соседних кадров
        
        Args:
            frames: Список ПОЛНЫХ кадров из extract_frames()
        
        Returns:
            Список уникальных слайдов (с ПОЛНЫМИ кадрами)
        """
        if not frames:
            return []
        
        slides = []
        
        # Первый кадр всегда добавляем (ПОЛНЫЙ!)
        first_frame, first_time, first_num = frames[0]
        slides.append(Slide(first_frame.copy(), first_time, first_num))
        
        logger.info(f"Детектирование смены слайдов (порог SSIM: {self.threshold})...")
        logger.info(f"Анализ области: {self.get_region_description()}")
        
        # Для сравнения обрезаем первый кадр
        prev_frame_cropped = self._crop_frame_region(first_frame)
        
        for i in range(1, len(frames)):
            current_frame, current_time, current_num = frames[i]
            
            # Для сравнения обрезаем текущий кадр
            current_frame_cropped = self._crop_frame_region(current_frame)
            
            # Сравниваем ОБРЕЗАННЫЕ кадры (без лектора)
            similarity = self.compare_frames(prev_frame_cropped, current_frame_cropped)
            
            # Если сходство ниже порога - это новый слайд
            if similarity < self.threshold:
                # Проверяем минимальную длительность слайда
                if current_time - slides[-1].timestamp >= MIN_SLIDE_DURATION:
                    # Сохраняем ПОЛНЫЙ кадр!
                    slides.append(Slide(current_frame.copy(), current_time, current_num))
                    logger.info(f"Найден новый слайд #{len(slides)} на {current_time:.2f}s (SSIM: {similarity:.3f})")
                    prev_frame_cropped = current_frame_cropped
            
            if i % 100 == 0:
                logger.info(f"Проанализировано: {i}/{len(frames)} кадров")
        
        logger.info(f"Всего найдено уникальных слайдов: {len(slides)}")
        return slides
    
    def save_slides(self, slides: List[Slide], output_dir: str) -> List[Tuple[str, float]]:
        """
        Сохраняет слайды в файлы
        
        Args:
            slides: Список слайдов
            output_dir: Директория для сохранения
        
        Returns:
            Список кортежей (путь_к_файлу, timestamp)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_slides = []
        
        logger.info(f"Сохранение {len(slides)} слайдов в {output_dir}...")
        
        for i, slide in enumerate(slides, start=1):
            filename = f"slide_{i:03d}.png"
            filepath = output_path / filename
            
            # Сохраняем ПОЛНЫЙ кадр (высокое качество)
            cv2.imwrite(str(filepath), slide.frame, [cv2.IMWRITE_PNG_COMPRESSION, 3])
            
            saved_slides.append((str(filepath), slide.timestamp))
            logger.info(f"Сохранён слайд {i}/{len(slides)}: {filename} (время: {slide.timestamp:.2f}s)")
        
        logger.info("✓ Все слайды сохранены")
        return saved_slides
    
    def process(self, output_dir: str) -> List[Tuple[str, float]]:
        """
        Полный цикл обработки видео
        
        Args:
            output_dir: Директория для сохранения слайдов
        
        Returns:
            Список кортежей (путь_к_слайду, timestamp)
        """
        logger.info("=" * 60)
        logger.info("НАЧАЛО ОБРАБОТКИ ВИДЕО")
        logger.info("=" * 60)
        
        # Извлечение кадров
        frames = self.extract_frames()
        
        # Детектирование смены слайдов
        slides = self.detect_slide_changes(frames)
        
        # Сохранение слайдов
        saved_slides = self.save_slides(slides, output_dir)
        
        # Освобождаем память
        self.cap.release()
        
        logger.info("=" * 60)
        logger.info("ОБРАБОТКА ЗАВЕРШЕНА")
        logger.info("=" * 60)
        
        return saved_slides


if __name__ == "__main__":
    # Простой тест
    print("VideoProcessor модуль загружен успешно!")
    print("Для тестирования запустите main.py с параметрами видео")

