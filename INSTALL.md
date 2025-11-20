# Инструкция по установке

## Требования к системе

- **macOS**: 10.14 (Mojave) или новее
- **Python**: 3.10 или новее
- **Процессор**: Оптимизировано для Apple Silicon (M1/M2/M3), но работает и на Intel

## Пошаговая установка

### 1. Проверка версии Python

Откройте Terminal и выполните:

```bash
python3 --version
```

Должна быть версия 3.10 или выше. Если нет, установите последнюю версию с [python.org](https://www.python.org/downloads/).

### 2. Создание виртуального окружения (рекомендуется)

```bash
cd lecture-slides-extractor
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Проверка установки

Проверьте, что модули загружены корректно:

```bash
python3 -c "import cv2; import numpy; import skimage; print('✓ Все модули установлены успешно!')"
```

## Оптимизация для Apple Silicon

### OpenCV оптимизация

Для максимальной производительности на M1/M2/M3 можно собрать OpenCV с поддержкой Accelerate Framework:

```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

Это обеспечит использование нативных оптимизаций Apple Silicon.

### Проверка использования нативной архитектуры

```bash
python3 -c "import platform; print(f'Архитектура: {platform.machine()}')"
```

Должно вывести `arm64` для Apple Silicon.

## Возможные проблемы

### Ошибка при установке opencv-python

Если возникает ошибка при установке OpenCV:

```bash
pip install --upgrade pip setuptools wheel
pip install opencv-python --no-cache-dir
```

### Медленная работа

Если обработка идёт медленно:
1. Убедитесь, что используете Python для arm64 (не Rosetta)
2. Увеличьте `--sample-rate` (например, до 2.0)
3. Выберите меньшую область анализа (например, угол вместо центра)

### Недостаточно памяти

Для больших видео (>2 часа):
1. Увеличьте `--sample-rate` до 2-3 секунд
2. Закройте другие приложения

## Обновление

Для обновления зависимостей:

```bash
pip install --upgrade -r requirements.txt
```

## Деинсталляция

Если используете виртуальное окружение:

```bash
deactivate
cd ..
rm -rf lecture-slides-extractor/venv
```

Или удалите пакеты:

```bash
pip uninstall opencv-python numpy scikit-image Pillow -y
```

