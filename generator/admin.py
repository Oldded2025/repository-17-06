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


# Register your models here.
