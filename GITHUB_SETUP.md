# Инструкция по загрузке на GitHub

## Шаг 1: Настройка Git (если еще не настроено)

Если вы хотите указать свое имя и email для коммитов:

```bash
git config --global user.name "Ваше Имя"
git config --global user.email "ваш.email@example.com"
```

## Шаг 2: Создание репозитория на GitHub

1. Откройте [GitHub.com](https://github.com) и войдите в свой аккаунт
2. Нажмите кнопку **"+"** в правом верхнем углу → **"New repository"**
3. Заполните форму:
   - **Repository name**: `lecture-slides-extractor` (или любое другое имя)
   - **Description**: "Extract slides from lecture videos and match with transcript text"
   - **Visibility**: Выберите Public или Private
   - **НЕ** ставьте галочки на "Initialize with README", "Add .gitignore", "Choose a license" (у нас уже есть эти файлы)
4. Нажмите **"Create repository"**

## Шаг 3: Подключение локального репозитория к GitHub

После создания репозитория GitHub покажет инструкции. Выполните команды:

```bash
cd "/Users/soloveev/Documents/Проекты/Cursor/My OS/lecture-slides-extractor"

# Добавьте удаленный репозиторий (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/lecture-slides-extractor.git

# Или если используете SSH:
# git remote add origin git@github.com:YOUR_USERNAME/lecture-slides-extractor.git

# Отправьте код на GitHub
git branch -M main
git push -u origin main
```

## Шаг 4: Проверка

Откройте ваш репозиторий на GitHub в браузере - вы должны увидеть все файлы проекта.

## Дополнительно: Добавление лицензии (опционально)

Если хотите добавить лицензию (например, MIT):

```bash
# Создайте файл LICENSE
# Затем:
git add LICENSE
git commit -m "Add MIT license"
git push
```

## Полезные команды для работы с GitHub

```bash
# Проверить статус
git status

# Посмотреть удаленные репозитории
git remote -v

# Отправить изменения
git push

# Получить изменения
git pull

# Посмотреть историю коммитов
git log --oneline
```

