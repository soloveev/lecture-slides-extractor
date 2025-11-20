#!/usr/bin/env python3
"""
Тест исправления SSIM
"""

import cv2
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.video_processor import VideoProcessor

def test_fixed_ssim():
    """Тест исправленного SSIM"""
    
    slides_dir = Path("materials/1_1 decomposing /2.1 Понимание бизнес-задачи_slides")
    
    slide6 = cv2.imread(str(slides_dir / "slide_006.png"))
    slide7 = cv2.imread(str(slides_dir / "slide_007.png"))
    slide8 = cv2.imread(str(slides_dir / "slide_008.png"))
    
    if slide6 is None or slide7 is None or slide8 is None:
        print("❌ Ошибка: не удалось загрузить слайды")
        return
    
    video_path = "materials/1_1 decomposing /2.1 Понимание бизнес-задачи.mp4"
    processor = VideoProcessor(
        video_path=video_path,
        sample_rate=2.0,
        threshold=0.92,
        crop_ratio=0.30
    )
    
    # Обрезаем слайды
    crop6 = processor.crop_center_region(slide6)
    crop7 = processor.crop_center_region(slide7)
    crop8 = processor.crop_center_region(slide8)
    
    print("=" * 80)
    print("ТЕСТ ИСПРАВЛЕННОГО SSIM")
    print("=" * 80)
    
    # Сравниваем через исправленный метод
    sim_6_7 = processor.compare_frames(crop6, crop7)
    sim_7_8 = processor.compare_frames(crop7, crop8)
    sim_6_8 = processor.compare_frames(crop6, crop8)
    
    print(f"SSIM (6 vs 7): {sim_6_7:.6f}")
    print(f"SSIM (7 vs 8): {sim_7_8:.6f}")
    print(f"SSIM (6 vs 8): {sim_6_8:.6f}")
    
    threshold = 0.92
    print(f"\nПорог: {threshold}")
    print(f"6 vs 7 >= порог: {sim_6_7 >= threshold} ({'✅ ОДИНАКОВЫЕ' if sim_6_7 >= threshold else '❌ РАЗНЫЕ'})")
    print(f"7 vs 8 >= порог: {sim_7_8 >= threshold} ({'✅ ОДИНАКОВЫЕ' if sim_7_8 >= threshold else '❌ РАЗНЫЕ'})")
    print(f"6 vs 8 >= порог: {sim_6_8 >= threshold} ({'✅ ОДИНАКОВЫЕ' if sim_6_8 >= threshold else '❌ РАЗНЫЕ'})")
    
    processor.cap.release()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_fixed_ssim()

