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


# Create your models here.
