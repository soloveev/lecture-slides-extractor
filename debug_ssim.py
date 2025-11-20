#!/usr/bin/env python3
"""
Детальный тест SSIM для понимания проблемы
"""

import cv2
import numpy as np
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
import sys

def crop_bottom_left(frame, ratio=0.30):
    """Обрезка левого нижнего угла"""
    height, width = frame.shape[:2]
    crop_width = int(width * ratio)
    crop_height = int(height * ratio)
    x_start = 0
    y_start = height - crop_height
    return frame[y_start:y_start+crop_height, x_start:x_start+crop_width]

def test_ssim_detailed():
    """Детальный тест SSIM"""
    
    slides_dir = Path("materials/1_1 decomposing /2.1 Понимание бизнес-задачи_slides")
    
    slide6 = cv2.imread(str(slides_dir / "slide_006.png"))
    slide7 = cv2.imread(str(slides_dir / "slide_007.png"))
    
    if slide6 is None or slide7 is None:
        print("❌ Ошибка: не удалось загрузить слайды")
        return
    
    crop6 = crop_bottom_left(slide6)
    crop7 = crop_bottom_left(slide7)
    
    print("=" * 80)
    print("АНАЛИЗ SSIM")
    print("=" * 80)
    
    # Конвертируем в grayscale
    gray6 = cv2.cvtColor(crop6, cv2.COLOR_BGR2GRAY)
    gray7 = cv2.cvtColor(crop7, cv2.COLOR_BGR2GRAY)
    
    print(f"Размер gray6: {gray6.shape}, dtype: {gray6.dtype}, min: {gray6.min()}, max: {gray6.max()}")
    print(f"Размер gray7: {gray7.shape}, dtype: {gray7.dtype}, min: {gray7.min()}, max: {gray7.max()}")
    
    # Проверяем, одинаковы ли размеры
    if gray6.shape != gray7.shape:
        print(f"⚠ Размеры разные! gray6: {gray6.shape}, gray7: {gray7.shape}")
        gray7 = cv2.resize(gray7, (gray6.shape[1], gray6.shape[0]))
        print(f"  После resize gray7: {gray7.shape}")
    
    # Вычисляем разницу
    diff = np.abs(gray6.astype(np.float32) - gray7.astype(np.float32))
    print(f"\nРазница между кадрами:")
    print(f"  Средняя разница: {diff.mean():.6f}")
    print(f"  Максимальная разница: {diff.max():.6f}")
    print(f"  Пикселей с разницей > 0: {np.count_nonzero(diff)}")
    print(f"  Пикселей с разницей > 1: {np.count_nonzero(diff > 1)}")
    print(f"  Пикселей с разницей > 5: {np.count_nonzero(diff > 5)}")
    print(f"  Пикселей с разницей > 10: {np.count_nonzero(diff > 10)}")
    
    # Тест 1: SSIM с полным изображением
    print("\n" + "-" * 80)
    print("ТЕСТ 1: SSIM с full=True")
    print("-" * 80)
    try:
        similarity1, ssim_map1 = ssim(gray6, gray7, full=True)
        print(f"SSIM: {similarity1:.10f}")
        print(f"SSIM map shape: {ssim_map1.shape}")
        print(f"SSIM map min: {ssim_map1.min():.10f}, max: {ssim_map1.max():.10f}, mean: {ssim_map1.mean():.10f}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: SSIM с full=False
    print("\n" + "-" * 80)
    print("ТЕСТ 2: SSIM с full=False")
    print("-" * 80)
    try:
        similarity2 = ssim(gray6, gray7, full=False)
        print(f"SSIM: {similarity2:.10f}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 3: SSIM с data_range
    print("\n" + "-" * 80)
    print("ТЕСТ 3: SSIM с data_range=255")
    print("-" * 80)
    try:
        similarity3 = ssim(gray6, gray7, data_range=255)
        print(f"SSIM: {similarity3:.10f}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 4: SSIM с win_size
    print("\n" + "-" * 80)
    print("ТЕСТ 4: SSIM с win_size=7")
    print("-" * 80)
    try:
        similarity4 = ssim(gray6, gray7, win_size=7)
        print(f"SSIM: {similarity4:.10f}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 5: Проверка на идентичность
    print("\n" + "-" * 80)
    print("ТЕСТ 5: Проверка на полную идентичность")
    print("-" * 80)
    are_identical = np.array_equal(gray6, gray7)
    print(f"Кадры полностью идентичны: {are_identical}")
    
    if not are_identical:
        # Находим координаты разных пикселей
        diff_mask = gray6 != gray7
        diff_coords = np.where(diff_mask)
        print(f"Количество разных пикселей: {len(diff_coords[0])}")
        if len(diff_coords[0]) > 0:
            print(f"Первые 10 координат разных пикселей:")
            for i in range(min(10, len(diff_coords[0]))):
                y, x = diff_coords[0][i], diff_coords[1][i]
                val6 = gray6[y, x]
                val7 = gray7[y, x]
                print(f"  ({y}, {x}): {val6} vs {val7} (разница: {abs(int(val6) - int(val7))})")
    
    # Тест 6: Нормализация и повторный SSIM
    print("\n" + "-" * 80)
    print("ТЕСТ 6: SSIM с нормализованными изображениями")
    print("-" * 80)
    try:
        gray6_norm = gray6.astype(np.float64) / 255.0
        gray7_norm = gray7.astype(np.float64) / 255.0
        similarity6 = ssim(gray6_norm, gray7_norm, data_range=1.0)
        print(f"SSIM (нормализованные): {similarity6:.10f}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_ssim_detailed()

