from django.urls import path
from . import views

app_name = "generator"

urlpatterns = [
    path("", views.index, name="index"),
    path("history/", views.history, name="history"),
    path("history/clear/", views.clear_history, name="clear_history"),
]