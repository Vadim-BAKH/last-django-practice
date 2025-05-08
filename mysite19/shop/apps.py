"""
Конфигурация приложения 'shop'.

Определяет настройки приложения для интеграции с Django.
"""

from django.apps import AppConfig


class ShopConfig(AppConfig):
    """
    Класс конфигурации приложения 'shop'.

    Атрибуты:
        default_auto_field (str):
        Тип поля для автоматического создания первичных ключей.
        name (str): Имя приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"
