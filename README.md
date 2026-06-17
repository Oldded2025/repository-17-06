# Генератор паролей на Django

Пошаговая инструкция по созданию проекта с нуля.

---

## Шаг 1: Подготовка проекта

### 1.1 Создайте репозиторий

```bash
# Создайте папку проекта
mkdir password_generator
cd password_generator

# Инициализируйте git
git init
```

### 1.2 Создайте .gitignore

Файл: `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
*.egg

# Virtual environment
venv/
env/
.env/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### 1.3 Создайте виртуальное окружение

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> **Важно:** Всегда активируйте виртуальное окружение перед работой с проектом!

### 1.4 Установите Django и создайте requirements.txt

```bash
pip install django

# Сохраните зависимости
pip freeze > requirements.txt
```

Содержимое `requirements.txt`:
```
asgiref==3.11.1
Django==6.0.6
sqlparse==0.5.5
tzdata==2026.2
```

> **Совет:** Команда `pip freeze > requirements.txt` сохраняет все установленные пакеты. Для установки на другом компьютере: `pip install -r requirements.txt`

---

## Шаг 2: Создание Django проекта

### 2.1 Создайте проект

```bash
django-admin startproject config .
```

Структура после команды:
```
password_generator/
├── config/
│   ├── __init__.py
│   ├── settings.py      # Настройки проекта
│   ├── urls.py          # Главные маршруты
│   └── wsgi.py
└── manage.py            # Утилита управления
```

### 2.2 Создайте приложение

```bash
python manage.py startapp generator
```

> **Разница:** `config` — это проект (настройки), `generator` — приложение (логика генерации паролей). В одном проекте может быть много приложений.

---

## Шаг 3: Настройка проекта

### 3.1 Зарегистрируйте приложение

Файл: `config/settings.py`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'generator',  # Добавьте эту строку
]
```

### 3.2 Настройте язык (опционально)

```python
# config/settings.py
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
```

---

## Шаг 4: Создание модели

### 4.1 Определите модель

Файл: `generator/models.py`

```python
from django.db import models
from django.utils import timezone


class PasswordHistory(models.Model):
    """Модель для хранения истории сгенерированных паролей"""

    password = models.CharField(max_length=255, verbose_name="Пароль")
    length = models.IntegerField(verbose_name="Длина пароля")
    use_uppercase = models.BooleanField(default=True, verbose_name="Заглавные буквы")
    use_lowercase = models.BooleanField(default=True, verbose_name="Строчные буквы")
    use_digits = models.BooleanField(default=True, verbose_name="Цифры")
    use_symbols = models.BooleanField(default=False, verbose_name="Спецсимволы")
    exclude_ambiguous = models.BooleanField(default=False, verbose_name="Исключить неоднозначные")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "История пароля"
        verbose_name_plural = "История паролей"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.password} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
```

> **Что такое модель?** Модель — это описание таблицы в базе данных. Каждое поле модели становится столбцом таблицы.

### 4.2 Создайте и примените миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

> **Миграции** — это система версионирования базы данных. `makemigrations` создает файл миграции, `migrate` применяет его к БД.

---

## Шаг 5: Админка

### 5.1 Зарегистрируйте модель

Файл: `generator/admin.py`

```python
from django.contrib import admin
from .models import PasswordHistory


@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "password", "length", "use_uppercase", "use_lowercase",
        "use_digits", "use_symbols", "exclude_ambiguous", "created_at"
    )
    list_filter = ("use_uppercase", "use_lowercase", "use_digits", "use_symbols", "created_at")
    search_fields = ("password",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
```

### 5.2 Создайте суперпользователя

```bash
python manage.py createsuperuser
```

---

## Шаг 6: Логика генерации паролей

### 6.1 Напишите views

Файл: `generator/views.py`

```python
import secrets
import string

from django.shortcuts import render, redirect
from django.contrib import messages

from .models import PasswordHistory

# Наборы символов
UPPERCASE = string.ascii_uppercase      # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWERCASE = string.ascii_lowercase      # 'abcdefghijklmnopqrstuvwxyz'
DIGITS = string.digits                  # '0123456789'
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
AMBIGUOUS = "Il1O0"                     # Похожие друг на друга символы


def generate_password(length, use_uppercase, use_lowercase, use_digits, use_symbols, exclude_ambiguous):
    """Генерация пароля с заданными параметрами"""

    characters = ""

    if use_uppercase:
        characters += UPPERCASE
    if use_lowercase:
        characters += LOWERCASE
    if use_digits:
        characters += DIGITS
    if use_symbols:
        characters += SYMBOLS

    # Если ничего не выбрано — используем строчные + цифры
    if not characters:
        characters = LOWERCASE + DIGITS

    # Убираем неоднозначные символы
    if exclude_ambiguous:
        characters = "".join(c for c in characters if c not in AMBIGUOUS)

    # Генерируем пароль
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


def index(request):
    """Главная страница с формой генерации пароля"""
    password = None
    length = 12

    if request.method == "POST":
        # Получаем данные из формы
        try:
            length = int(request.POST.get("length", 12))
            length = max(4, min(length, 128))  # Ограничиваем 4-128
        except ValueError:
            length = 12

        use_uppercase = "uppercase" in request.POST
        use_lowercase = "lowercase" in request.POST
        use_digits = "digits" in request.POST
        use_symbols = "symbols" in request.POST
        exclude_ambiguous = "exclude_ambiguous" in request.POST

        # Генерируем пароль
        password = generate_password(
            length, use_uppercase, use_lowercase,
            use_digits, use_symbols, exclude_ambiguous
        )

        # Сохраняем в историю
        PasswordHistory.objects.create(
            password=password,
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols,
            exclude_ambiguous=exclude_ambiguous,
        )

        messages.success(request, "Пароль успешно сгенерирован!")

    return render(request, "generator/index.html", {"password": password, "length": length})


def history(request):
    """Страница с историей паролей"""
    passwords = PasswordHistory.objects.all()[:50]
    return render(request, "generator/history.html", {"passwords": passwords})


def clear_history(request):
    """Очистка истории паролей"""
    if request.method == "POST":
        PasswordHistory.objects.all().delete()
        messages.success(request, "История очищена!")
    return redirect("history")
```

> **Почему `secrets`, а не `random`?** Модуль `secrets` криптографически безопасен — он использует системный генератор случайных чисел, что важно для паролей.

---

## Шаг 7: Маршруты (URLs)

### 7.1 Маршруты приложения

Создайте файл: `generator/urls.py`

```python
from django.urls import path
from . import views

app_name = "generator"

urlpatterns = [
    path("", views.index, name="index"),
    path("history/", views.history, name="history"),
    path("history/clear/", views.clear_history, name="clear_history"),
]
```

### 7.2 Подключите к проекту

Файл: `config/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('generator.urls')),
]
```

---

## Шаг 8: Шаблоны (HTML)

### 8.1 Создайте структуру папок

```
generator/
└── templates/
    └── generator/
        ├── base.html
        ├── index.html
        └── history.html
```

### 8.2 Базовый шаблон

Файл: `generator/templates/generator/base.html`

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Генератор паролей{% endblock %}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        header { text-align: center; color: white; margin-bottom: 30px; }
        header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        nav {
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        nav a {
            color: white;
            text-decoration: none;
            margin: 0 15px;
            padding: 8px 16px;
            border-radius: 5px;
        }
        nav a:hover { background: rgba(255, 255, 255, 0.3); }
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
        }
        .checkbox-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .btn {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            cursor: pointer;
        }
        .password-result {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: center;
        }
        .password-text {
            font-family: 'Courier New', monospace;
            font-size: 1.5rem;
            word-break: break-all;
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 8px;
        }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #f8f9fa; font-weight: 600; }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            margin: 2px;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            background: #d4edda;
            color: #155724;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Генератор паролей</h1>
            <p>Создавайте надежные пароли с настройками под себя</p>
        </header>

        <nav>
            <a href="{% url 'generator:index' %}">Главная</a>
            <a href="{% url 'generator:history' %}">История</a>
            <a href="/admin/">Админка</a>
        </nav>

        {% if messages %}
            {% for message in messages %}
            <div class="message">{{ message }}</div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

### 8.3 Главная страница

Файл: `generator/templates/generator/index.html`

```html
{% extends "generator/base.html" %}

{% block content %}
<div class="card">
    <h2 style="margin-bottom: 20px;">Настройка пароля</h2>

    <form method="post">
        {% csrf_token %}

        <div class="form-group">
            <label for="length">Длина пароля</label>
            <input type="number" id="length" name="length"
                   value="{{ length }}" min="4" max="128" required>
        </div>

        <div class="form-group">
            <label>Набор символов</label>
            <div class="checkbox-group">
                <label class="checkbox-item">
                    <input type="checkbox" name="lowercase" checked>
                    <span>Строчные буквы (a-z)</span>
                </label>
                <label class="checkbox-item">
                    <input type="checkbox" name="uppercase" checked>
                    <span>Заглавные буквы (A-Z)</span>
                </label>
                <label class="checkbox-item">
                    <input type="checkbox" name="digits" checked>
                    <span>Цифры (0-9)</span>
                </label>
                <label class="checkbox-item">
                    <input type="checkbox" name="symbols">
                    <span>Спецсимволы (!@#$%^&*)</span>
                </label>
            </div>
        </div>

        <div class="form-group">
            <div class="checkbox-group">
                <label class="checkbox-item">
                    <input type="checkbox" name="exclude_ambiguous">
                    <span>Исключить неоднозначные (I, l, 1, O, 0)</span>
                </label>
            </div>
        </div>

        <button type="submit" class="btn">Сгенерировать пароль</button>
    </form>

    {% if password %}
    <div class="password-result">
        <h3>Ваш пароль:</h3>
        <div class="password-text" id="password-text">{{ password }}</div>
        <button class="btn" style="margin-top: 15px;" onclick="copyPassword()">
            Копировать
        </button>
    </div>
    {% endif %}
</div>

<script>
function copyPassword() {
    const password = document.getElementById('password-text').textContent;
    navigator.clipboard.writeText(password).then(() => {
        alert('Пароль скопирован!');
    });
}
</script>
{% endblock %}
```

### 8.4 Страница истории

Файл: `generator/templates/generator/history.html`

```html
{% extends "generator/base.html" %}

{% block title %}История паролей{% endblock %}

{% block content %}
<div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>История паролей</h2>
        {% if passwords %}
        <form method="post" action="{% url 'generator:clear_history' %}">
            {% csrf_token %}
            <button type="submit" class="btn" style="background: #ff6b6b;"
                    onclick="return confirm('Очистить историю?')">
                Очистить
            </button>
        </form>
        {% endif %}
    </div>

    {% if passwords %}
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Пароль</th>
                <th>Длина</th>
                <th>Настройки</th>
                <th>Дата</th>
            </tr>
        </thead>
        <tbody>
            {% for item in passwords %}
            <tr>
                <td>{{ forloop.counter }}</td>
                <td><code>{{ item.password }}</code></td>
                <td>{{ item.length }}</td>
                <td>
                    {% if item.use_lowercase %}<span class="badge badge-success">a-z</span>{% endif %}
                    {% if item.use_uppercase %}<span class="badge badge-success">A-Z</span>{% endif %}
                    {% if item.use_digits %}<span class="badge badge-success">0-9</span>{% endif %}
                    {% if item.use_symbols %}<span class="badge badge-success">!@#$</span>% endif %}
                </td>
                <td>{{ item.created_at|date:"d.m.Y H:i" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p style="text-align: center; padding: 40px; color: #6c757d;">
        История пуста. <a href="{% url 'generator:index' %}">Сгенерируйте пароль!</a>
    </p>
    {% endif %}
</div>
{% endblock %}
```

---

## Шаг 9: Запуск и проверка

### 9.1 Запустите сервер

```bash
python manage.py runserver
```

### 9.2 Проверьте работу

- **Главная:** http://127.0.0.1:8000/
- **История:** http://127.0.0.1:8000/history/
- **Админка:** http://127.0.0.1:8000/admin/

---

## Шаг 10: Коммит в репозиторий

```bash
git add .
git commit -m "Initial commit: password generator project"
```

---

## Полезные команды

| Команда | Описание |
|---------|----------|
| `python manage.py runserver` | Запуск сервера разработки |
| `python manage.py makemigrations` | Создание миграций |
| `python manage.py migrate` | Применение миграций |
| `python manage.py createsuperuser` | Создание админа |
| `python manage.py shell` | Интерактивная консоль Django |
| `pip freeze > requirements.txt` | Сохранение зависимостей |

---

## Итоговая структура проекта

```
password_generator/
├── .gitignore
├── requirements.txt
├── manage.py
├── db.sqlite3
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── generator/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   │   └── __init__.py
│   └── templates/
│       └── generator/
│           ├── base.html
│           ├── index.html
│           └── history.html
└── venv/
```

---

## Идеи для расширения

1. **Авторизация** — регистрация пользователей, личная история
2. **API** — DRF для генерации паролей через API
3. **Экспорт** — скачать историю в CSV/JSON
4. **Оценка надежности** — показывать сложность пароля
5. **Категории** — привязка паролей к сервисам (email, банк и т.д.)
