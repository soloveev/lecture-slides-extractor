#!/usr/bin/env python3
"""
Тестовый скрипт для отладки проблемы с одинаковыми слайдами 6, 7, 8
"""

import cv2
import numpy as np
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
import sys

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.video_processor import VideoProcessor

def crop_bottom_left(frame, ratio=0.30):
    """Обрезка левого нижнего угла (как в VideoProcessor)"""
    height, width = frame.shape[:2]
    crop_width = int(width * ratio)
    crop_height = int(height * ratio)
    x_start = 0
    y_start = height - crop_height
    return frame[y_start:y_start+crop_height, x_start:x_start+crop_width]

def compare_frames_ssim(frame1, frame2):
    """Сравнение кадров через SSIM"""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    if gray1.shape != gray2.shape:
        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
    
    similarity, _ = ssim(gray1, gray2, full=True)
    return similarity

def test_slides_6_7_8():
    """Тест слайдов 6, 7, 8"""
    
    slides_dir = Path("materials/1_1 decomposing /2.1 Понимание бизнес-задачи_slides")
    
    # Загружаем слайды
    slide6 = cv2.imread(str(slides_dir / "slide_006.png"))
    slide7 = cv2.imread(str(slides_dir / "slide_007.png"))
    slide8 = cv2.imread(str(slides_dir / "slide_008.png"))
    
    if slide6 is None or slide7 is None or slide8 is None:
        print("❌ Ошибка: не удалось загрузить слайды")
        return
    
    print("=" * 80)
    print("ТЕСТ 1: Сравнение ПОЛНЫХ слайдов")
    print("=" * 80)
    
    # Сравнение полных слайдов
    sim_6_7_full = compare_frames_ssim(slide6, slide7)
    sim_7_8_full = compare_frames_ssim(slide7, slide8)
    sim_6_8_full = compare_frames_ssim(slide6, slide8)
    
    print(f"SSIM (6 vs 7, полные): {sim_6_7_full:.6f}")
    print(f"SSIM (7 vs 8, полные): {sim_7_8_full:.6f}")
    print(f"SSIM (6 vs 8, полные): {sim_6_8_full:.6f}")
    
    print("\n" + "=" * 80)
    print("ТЕСТ 2: Сравнение ОБРЕЗАННЫХ областей (левый нижний угол 30%)")
    print("=" * 80)
    
    # Обрезка левого нижнего угла
    crop6 = crop_bottom_left(slide6)
    crop7 = crop_bottom_left(slide7)
    crop8 = crop_bottom_left(slide8)
    
    print(f"Размер обрезки slide6: {crop6.shape}")
    print(f"Размер обрезки slide7: {crop7.shape}")
    print(f"Размер обрезки slide8: {crop8.shape}")
    
    # Сравнение обрезанных областей
    sim_6_7_crop = compare_frames_ssim(crop6, crop7)
    sim_7_8_crop = compare_frames_ssim(crop7, crop8)
    sim_6_8_crop = compare_frames_ssim(crop6, crop8)
    
    print(f"\nSSIM (6 vs 7, обрезка): {sim_6_7_crop:.6f}")
    print(f"SSIM (7 vs 8, обрезка): {sim_7_8_crop:.6f}")
    print(f"SSIM (6 vs 8, обрезка): {sim_6_8_crop:.6f}")
    
    # Сохраняем обрезанные области для визуального сравнения
    debug_dir = Path("debug_crops")
    debug_dir.mkdir(exist_ok=True)
    cv2.imwrite(str(debug_dir / "crop_006.png"), crop6)
    cv2.imwrite(str(debug_dir / "crop_007.png"), crop7)
    cv2.imwrite(str(debug_dir / "crop_008.png"), crop8)
    print(f"\n✓ Обрезанные области сохранены в {debug_dir}/")
    
    print("\n" + "=" * 80)
    print("ТЕСТ 3: Проверка различий в обрезанных областях")
    print("=" * 80)
    
    # Вычисляем разницу
    diff_6_7 = cv2.absdiff(crop6, crop7)
    diff_7_8 = cv2.absdiff(crop7, crop8)
    
    # Подсчитываем количество разных пикселей
    diff_pixels_6_7 = np.count_nonzero(diff_6_7)
    diff_pixels_7_8 = np.count_nonzero(diff_7_8)
    total_pixels = crop6.shape[0] * crop6.shape[1] * crop6.shape[2]
    
    print(f"Разных пикселей (6 vs 7): {diff_pixels_6_7} из {total_pixels} ({100*diff_pixels_6_7/total_pixels:.2f}%)")
    print(f"Разных пикселей (7 vs 8): {diff_pixels_7_8} из {total_pixels} ({100*diff_pixels_7_8/total_pixels:.2f}%)")
    
    # Сохраняем разницу
    cv2.imwrite(str(debug_dir / "diff_6_7.png"), diff_6_7)
    cv2.imwrite(str(debug_dir / "diff_7_8.png"), diff_7_8)
    print(f"✓ Карты различий сохранены в {debug_dir}/")
    
    print("\n" + "=" * 80)
    print("ТЕСТ 4: Проверка через VideoProcessor")
    print("=" * 80)
    
    video_path = "materials/1_1 decomposing /2.1 Понимание бизнес-задачи.mp4"
    if not Path(video_path).exists():
        print(f"⚠ Видео не найдено: {video_path}")
        return
    
    processor = VideoProcessor(
        video_path=video_path,
        sample_rate=2.0,
        threshold=0.92,
        crop_ratio=0.30
    )
    
    # Обрезаем через VideoProcessor
    crop6_proc = processor.crop_center_region(slide6)
    crop7_proc = processor.crop_center_region(slide7)
    crop8_proc = processor.crop_center_region(slide8)
    
    sim_6_7_proc = processor.compare_frames(crop6_proc, crop7_proc)
    sim_7_8_proc = processor.compare_frames(crop7_proc, crop8_proc)
    
    print(f"SSIM через VideoProcessor (6 vs 7): {sim_6_7_proc:.6f}")
    print(f"SSIM через VideoProcessor (7 vs 8): {sim_7_8_proc:.6f}")
    
    processor.cap.release()
    
    print("\n" + "=" * 80)
    print("ВЫВОДЫ")
    print("=" * 80)
    
    threshold = 0.92
    if sim_6_7_crop >= threshold and sim_7_8_crop >= threshold:
        print("✅ Обрезанные области ОДИНАКОВЫЕ (SSIM >= 0.92)")
        print("   Проблема в логике обновления prev_frame_cropped!")
    elif sim_6_7_crop < threshold or sim_7_8_crop < threshold:
        print("❌ Обрезанные области РАЗНЫЕ (SSIM < 0.92)")
        print("   Возможные причины:")
        print("   1. В левом нижнем углу есть различия (анимация, тень, шум)")
        print("   2. Проблема с обрезкой (разные координаты)")
        print("   3. Проблема с SSIM (неправильное сравнение)")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_slides_6_7_8()

