"""
Конфигурация по умолчанию для Lecture Slides Extractor
"""

# Параметры обработки видео
DEFAULT_SAMPLE_RATE = 1.0  # Анализировать 1 кадр в 1 секунду (чаще = ловим быстрые переключения слайдов)
DEFAULT_THRESHOLD = 0.92   # Порог SSIM для детектирования смены слайда (строже!)

# Варианты области анализа
CROP_REGION_BOTTOM_LEFT = "bottom_left"      # Левый нижний угол (по умолчанию)
CROP_REGION_BOTTOM_RIGHT = "bottom_right"    # Правый нижний угол
CROP_REGION_TOP_RIGHT = "top_right"          # Правый верхний угол
CROP_REGION_TOP_LEFT = "top_left"            # Левый верхний угол
CROP_REGION_CENTER = "center"                # Центр (небольшая область)

DEFAULT_CROP_REGION = CROP_REGION_BOTTOM_LEFT  # По умолчанию левый нижний угол

# Размеры областей анализа (в процентах от размера кадра)
CROP_SIZE_CORNER = 0.30  # 30% для угловых областей
CROP_SIZE_CENTER = 0.50  # 50% для центральной области (чтобы лектор не попал)

# Параметры выходных файлов
DEFAULT_OUTPUT_FILE = "output.md"
DEFAULT_SLIDES_DIR = "slides"
SLIDE_IMAGE_FORMAT = "png"
SLIDE_IMAGE_QUALITY = 95

# Параметры обработки
MIN_SLIDE_DURATION = 30  # Минимальная длительность слайда в секундах (для лекций обычно слайд держится долго)
MAX_FRAMES_IN_MEMORY = 100  # Максимальное количество кадров в памяти

# Логирование
LOG_LEVEL = "INFO"

