# Автоматический режим обработки

Простой способ обработки видео из папок.

## Как это работает

1. Создайте папку с видео и транскриптом
2. Запустите программу, указав путь к папке
3. Получите результат в той же папке

## Пример использования

### 1. Подготовка

Создайте структуру:

```
material/
└── one-one-decomposition/
    ├── lecture.mp4          ← Ваше видео
    └── transcript.txt       ← Ваш транскрипт
```

### 2. Запуск

```bash
python3 auto_process.py material/one-one-decomposition
```

### 3. Результат

После обработки в папке появятся:

```
material/
└── one-one-decomposition/
    ├── lecture.mp4
    ├── transcript.txt
    ├── lecture.md           ← Markdown документ
    └── lecture_slides/      ← Папка со слайдами
        ├── slide_001.png
        ├── slide_002.png
        └── ...
```

## Команды

### Базовый запуск

```bash
python3 auto_process.py material/one-one-decomposition
```

### С параметрами

```bash
python3 auto_process.py material/one-one-decomposition \
  --sample-rate 1.0 \
  --threshold 0.92
```

### Быстрая обработка

```bash
python3 auto_process.py material/one-one-decomposition \
  --sample-rate 2.0 \
  --threshold 0.90
```

### Точная обработка

```bash
python3 auto_process.py material/one-one-decomposition \
  --sample-rate 0.5 \
  --threshold 0.95
```

### Автоматическая перезапись (без подтверждения)

```bash
python3 auto_process.py material/one-one-decomposition --force
```

Флаг `--force` автоматически перезаписывает существующие файлы без запроса подтверждения.

## Требования к папке

### Обязательно должны быть:

- **Один видеофайл** (mp4, mov, avi, mkv, m4v)
- **Один текстовый файл** с транскриптом (txt)

### Программа автоматически:

- Найдёт видеофайл (первый найденный)
- Найдёт транскрипт (первый txt файл)
- Создаст MD файл с именем видео
- Создаст папку со слайдами с именем `{видео}_slides`

## Примеры

### Обработка лекции про декомпозицию

```bash
python3 auto_process.py material/one-one-decomposition
```

### Обработка лекции про Python

```bash
python3 auto_process.py material/python-basics
```

### Обработка с разных мест

```bash
# Из текущей папки
python3 auto_process.py ./my-lectures/lecture1

# Абсолютный путь
python3 auto_process.py /Users/user/Documents/lectures/week1
```

## Параметры

- `--sample-rate` - Как часто анализировать кадры (1.0 = каждую секунду, по умолчанию)
- `--threshold` - Насколько строго определять смену слайдов (0.92 = строго, по умолчанию)
- `--crop-region` - Область для анализа (bottom_left, bottom_right, top_right, top_left, center). Если не указано, будет предложен интерактивный выбор
- `--force` - Автоматически перезаписывать существующие файлы без подтверждения

**Примечание**: При запуске программа предложит выбрать область анализа (где НЕТ лектора). По умолчанию используется левый нижний угол (30%). Сохраняются полные кадры слайдов.

## Что если файл уже существует?

По умолчанию программа спросит:

```
⚠ Файл lecture.md уже существует
  Перезаписать? (y/n):
```

- Введите `y` - перезаписать
- Введите `n` - пропустить

Или используйте флаг `--force` для автоматической перезаписи без подтверждения:

```bash
python3 auto_process.py material/one-one-decomposition --force
```

## Быстрый доступ через алиас

Добавьте в `~/.zshrc` или `~/.bashrc`:

```bash
alias process-lecture='python3 /path/to/lecture-slides-extractor/auto_process.py'
```

Теперь можно запускать короче:

```bash
process-lecture material/one-one-decomposition
```

## Справка

```bash
python3 auto_process.py --help
```

## Примеры для разных случаев

### Видео с частой сменой слайдов

```bash
python3 auto_process.py material/fast-slides --sample-rate 0.5 --threshold 0.90
```

### Видео с редкой сменой слайдов

```bash
python3 auto_process.py material/slow-slides --sample-rate 2.0 --threshold 0.92
```

**Примечание**: При запуске программа предложит выбрать область анализа (где НЕТ лектора). Можно также указать через параметр `--crop-region`.

---

**Готово! Просто укажите папку и программа всё сделает сама.**

