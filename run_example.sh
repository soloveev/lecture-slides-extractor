#!/bin/bash
# Пример запуска Lecture Slides Extractor

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Lecture Slides Extractor - Пример${NC}"
echo -e "${BLUE}========================================${NC}"

# Проверка аргументов
if [ "$#" -ne 2 ]; then
    echo "Использование: $0 <видеофайл> <транскрипт>"
    echo ""
    echo "Пример:"
    echo "  $0 lecture.mp4 transcript.txt"
    echo ""
    exit 1
fi

VIDEO_FILE="$1"
TRANSCRIPT_FILE="$2"

# Проверка существования файлов
if [ ! -f "$VIDEO_FILE" ]; then
    echo "Ошибка: Видеофайл не найден: $VIDEO_FILE"
    exit 1
fi

if [ ! -f "$TRANSCRIPT_FILE" ]; then
    echo "Ошибка: Файл транскрипта не найден: $TRANSCRIPT_FILE"
    exit 1
fi

# Создание имени выходного файла на основе имени видео
BASENAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
OUTPUT_FILE="${BASENAME}_slides.md"
SLIDES_DIR="${BASENAME}_slides"

echo -e "${GREEN}Входные файлы:${NC}"
echo "  Видео: $VIDEO_FILE"
echo "  Транскрипт: $TRANSCRIPT_FILE"
echo ""
echo -e "${GREEN}Выходные файлы:${NC}"
echo "  Markdown: $OUTPUT_FILE"
echo "  Папка слайдов: $SLIDES_DIR/"
echo ""

# Запуск обработки
python3 src/main.py \
    --video "$VIDEO_FILE" \
    --transcript "$TRANSCRIPT_FILE" \
    --output "$OUTPUT_FILE" \
    --slides-dir "$SLIDES_DIR" \
    --sample-rate 1.0 \
    --threshold 0.85 \
    --crop-ratio 0.75

# Проверка успешности
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Обработка завершена успешно!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Результаты:"
    echo "  📄 Markdown: $OUTPUT_FILE"
    echo "  🖼️  Слайды: $SLIDES_DIR/"
    echo ""
    
    # Показываем количество слайдов
    if [ -d "$SLIDES_DIR" ]; then
        SLIDE_COUNT=$(ls -1 "$SLIDES_DIR"/*.png 2>/dev/null | wc -l | tr -d ' ')
        echo "  Извлечено слайдов: $SLIDE_COUNT"
    fi
else
    echo ""
    echo -e "❌ Ошибка при обработке"
    exit 1
fi

