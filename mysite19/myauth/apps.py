"""
Конфигурация приложения myauth.
"""

from django.apps import AppConfig


class MyauthConfig(AppConfig):
    """
    Класс конфигурации приложения myauth.

    Атрибуты:
        default_auto_field (str): Тип поля для автоматического создания первичных ключей.
        name (str): Имя приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "myauth"
