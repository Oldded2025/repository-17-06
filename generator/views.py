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
# Create your views here.
