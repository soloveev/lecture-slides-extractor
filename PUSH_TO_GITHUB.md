# Как загрузить код на GitHub

## Вариант 1: Использование Personal Access Token (рекомендуется)

### Шаг 1: Создайте Personal Access Token на GitHub

1. Откройте GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Нажмите **"Generate new token (classic)"**
3. Заполните:
   - **Note**: "lecture-slides-extractor"
   - **Expiration**: Выберите срок действия (например, 90 дней)
   - **Scopes**: Отметьте `repo` (полный доступ к репозиториям)
4. Нажмите **"Generate token"**
5. **ВАЖНО**: Скопируйте токен сразу (он показывается только один раз!)

### Шаг 2: Загрузите код

Выполните команду (GitHub попросит ввести username и password):
- **Username**: `soloveev`
- **Password**: Вставьте ваш Personal Access Token (НЕ ваш обычный пароль!)

```bash
cd "/Users/soloveev/Documents/Проекты/Cursor/My OS/lecture-slides-extractor"
git push -u origin main
```

### Шаг 3: Сохраните токен для будущего использования (опционально)

Чтобы не вводить токен каждый раз, можно использовать Git Credential Manager:

```bash
# macOS
git config --global credential.helper osxkeychain
```

## Вариант 2: Настройка SSH ключа

### Шаг 1: Проверьте, есть ли SSH ключ

```bash
ls -la ~/.ssh/id_*.pub
```

Если файлов нет, создайте новый ключ:

```bash
ssh-keygen -t ed25519 -C "ваш.email@example.com"
# Нажмите Enter для всех вопросов (или задайте пароль)
```

### Шаг 2: Добавьте SSH ключ на GitHub

1. Скопируйте публичный ключ:
```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

2. На GitHub: Settings → SSH and GPG keys → New SSH key
3. Вставьте ключ и сохраните

### Шаг 3: Измените remote на SSH и загрузите

```bash
cd "/Users/soloveev/Documents/Проекты/Cursor/My OS/lecture-slides-extractor"
git remote set-url origin git@github.com:soloveev/lecture-slides-extractor.git
git push -u origin main
```

## Вариант 3: Использование GitHub CLI

Если установлен GitHub CLI:

```bash
gh auth login
gh repo create lecture-slides-extractor --public --source=. --remote=origin --push
```

## Проверка

После успешной загрузки откройте в браузере:
https://github.com/soloveev/lecture-slides-extractor

Вы должны увидеть все файлы проекта!

