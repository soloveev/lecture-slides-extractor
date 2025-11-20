# Примеры использования

Практические примеры использования Lecture Slides Extractor для различных сценариев.

## Базовые примеры

### 1. Минимальная команда

```bash
python3 src/main.py --video lecture.mp4 --transcript transcript.txt
```

**Результат:**
- `output.md` - Markdown файл
- `slides/` - Папка с изображениями слайдов

---

### 2. Пользовательские выходные файлы

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --output "Лекция_1_Python.md" \
  --slides-dir "python_slides"
```

**Результат:**
- `Лекция_1_Python.md`
- `python_slides/` - Папка со слайдами

---

### 3. С заголовком

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --title "Введение в машинное обучение"
```

Markdown будет начинаться с заголовка: `# Введение в машинное обучение`

---

## Настройка качества и скорости

### 4. Быстрая обработка (для тестирования)

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --sample-rate 2.0 \
  --threshold 0.90
```

**Ожидаемое время:** ~50% от стандартного  
**Точность:** ~85%

---

### 5. Максимальная точность

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --sample-rate 0.5 \
  --threshold 0.95
```

**Ожидаемое время:** ~200% от стандартного  
**Точность:** ~97%

---

### 6. Сбалансированный режим (рекомендуется, по умолчанию)

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --sample-rate 1.0 \
  --threshold 0.92
```

Это параметры по умолчанию - можно не указывать.

**Примечание**: Область анализа фиксирована (левый нижний угол 30%) для исключения лектора. Сохраняются полные кадры слайдов.

---

## Специальные случаи

### 7. Видео с частой сменой слайдов

Для презентаций, где слайды меняются каждые 10-20 секунд:

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --sample-rate 0.5 \
  --threshold 0.90
```

---

### 8. Видео с редкой сменой слайдов

Для длинных объяснений на одном слайде (3-5 минут):

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --sample-rate 2.0 \
  --threshold 0.92
```

---

### 9. Обработка папки с видео и транскриптом

Если у вас есть папка с видео и транскриптом:

```bash
python3 auto_process.py "путь/к/папке" --force
```

Скрипт автоматически найдет видео и транскрипт и обработает их.

---

## Отладка и диагностика

### 11. Подробный вывод (verbose)

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --verbose
```

Выведет детальную информацию о процессе обработки.

---

## Пакетная обработка

### 12. Обработка нескольких видео

Создайте скрипт `batch_process.sh`:

```bash
#!/bin/bash

for video in lectures/*.mp4; do
    name=$(basename "$video" .mp4)
    python3 src/main.py \
        --video "$video" \
        --transcript "transcripts/${name}.txt" \
        --output "output/${name}_slides.md" \
        --slides-dir "output/${name}_slides"
    echo "Обработано: $name"
done
```

Запустите:
```bash
chmod +x batch_process.sh
./batch_process.sh
```

---

### 13. Обработка с разными параметрами

Если у вас видео разного качества:

```bash
# Для HD видео (1920x1080)
python3 src/main.py --video hd_lecture.mp4 --transcript hd.txt --sample-rate 1.0

# Для SD видео (640x480)
python3 src/main.py --video sd_lecture.mp4 --transcript sd.txt --sample-rate 0.5 --threshold 0.80
```

---

## Использование helper-скрипта

### 14. Простой запуск через скрипт

```bash
./run_example.sh lecture.mp4 transcript.txt
```

Автоматически создаст выходные файлы с именами на основе видео.

---

## Работа с разными форматами видео

### 15. MP4 видео

```bash
python3 src/main.py --video lecture.mp4 --transcript transcript.txt
```

### 16. MOV видео (часто с iPhone/Mac)

```bash
python3 src/main.py --video recording.mov --transcript transcript.txt
```

### 17. AVI видео

```bash
python3 src/main.py --video old_lecture.avi --transcript transcript.txt
```

---

## Оптимизация под конкретные нужды

### 18. Только извлечение слайдов (минимум текста)

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript empty.txt \
  --threshold 0.85
```

Создайте пустой `empty.txt` или с минимальным текстом.

---

### 19. Максимальное количество слайдов

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --threshold 0.88 \
  --sample-rate 0.5
```

Захватит даже небольшие изменения на слайдах.

---

### 20. Минимальное количество слайдов

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --threshold 0.95 \
  --sample-rate 2.0
```

Только явные смены слайдов.

---

## Комбинированные примеры

### 21. Быстрая обработка + вывод в папку курса

```bash
python3 src/main.py \
  --video lecture.mp4 \
  --transcript transcript.txt \
  --output "course/week1/lecture.md" \
  --slides-dir "course/week1/slides" \
  --sample-rate 1.5 \
  --title "Неделя 1: Введение"
```

---

### 22. Обработка длинного видео (>2 часов)

```bash
python3 src/main.py \
  --video long_webinar.mp4 \
  --transcript webinar_transcript.txt \
  --sample-rate 2.0 \
  --threshold 0.90
```

Оптимизировано для производительности.

---

## Проверка результатов

### 23. Проверка количества слайдов

```bash
python3 src/main.py --video lecture.mp4 --transcript transcript.txt
ls -1 slides/*.png | wc -l
```

### 24. Проверка размера выходных файлов

```bash
python3 src/main.py --video lecture.mp4 --transcript transcript.txt
du -sh output.md slides/
```

---

## Работа с путями

### 25. Абсолютные пути

```bash
python3 src/main.py \
  --video "/Users/user/Videos/lecture.mp4" \
  --transcript "/Users/user/Documents/transcript.txt" \
  --output "/Users/user/Output/result.md"
```

### 26. Относительные пути

```bash
cd my_project
python3 ../lecture-slides-extractor/src/main.py \
  --video ./videos/lecture.mp4 \
  --transcript ./transcripts/lecture.txt \
  --output ./output/lecture.md
```

---

## Типичные сценарии использования

### Сценарий 1: Обработка записи Zoom

```bash
python3 src/main.py \
  --video zoom_meeting.mp4 \
  --transcript zoom_transcript.txt \
  --sample-rate 1.5 \
  --threshold 0.92 \
  --title "Встреча команды 2024-01-15"
```

### Сценарий 2: Обработка YouTube лекции

```bash
# Сначала скачайте видео через yt-dlp
yt-dlp "https://youtube.com/watch?v=..." -o lecture.mp4

# Получите субтитры и конвертируйте в нужный формат
# Затем обработайте
python3 src/main.py \
  --video lecture.mp4 \
  --transcript lecture_transcript.txt \
  --output "YouTube_Lecture.md"
```

### Сценарий 3: Обработка учебного курса

```bash
for i in {1..10}; do
    python3 src/main.py \
        --video "course/lecture_$i.mp4" \
        --transcript "course/transcript_$i.txt" \
        --output "course/notes/lecture_$i.md" \
        --slides-dir "course/notes/slides_$i" \
        --title "Лекция $i"
done
```

---

## Советы по выбору параметров

### Когда увеличивать sample-rate:
- Видео очень длинное (>90 минут)
- Слайды меняются редко (>2 минут на слайд)
- Нужна быстрая обработка
- Ограничена оперативная память

### Когда уменьшать sample-rate:
- Слайды меняются быстро (<30 секунд)
- Важна максимальная точность
- Видео короткое (<30 минут)

### Когда увеличивать threshold:
- Слишком много дубликатов слайдов (увеличьте до 0.95)
- На слайдах есть анимации
- Нужны только явные смены слайдов

### Когда уменьшать threshold:
- Пропускаются важные слайды (уменьшите до 0.90)
- Изменения на слайдах минимальные
- Лучше больше, чем пропустить

**Примечание**: При запуске программа предложит выбрать область анализа (где НЕТ лектора). Можно также указать через параметр `--crop-region` (bottom_left, bottom_right, top_right, top_left, center).

---

## Полезные команды

### Проверка версии Python
```bash
python3 --version
```

### Проверка установленных пакетов
```bash
pip3 list | grep -E "opencv|numpy|scikit|Pillow"
```

### Получение справки
```bash
python3 src/main.py --help
```

### Информация о видео
```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,duration \
  -of default=noprint_wrappers=1 lecture.mp4
```

---

**Готовы начать? Выберите подходящий пример и адаптируйте под свои нужды!**

