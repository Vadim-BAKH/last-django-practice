"""
Сериализаторы для моделей Product и Order.

Обеспечивают преобразование данных моделей в формат JSON и обратно.
"""

from rest_framework import serializers

from .models import Order, Product


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product."""

    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_at",
            "created_by",
            "archived",
            "preview",
        )


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order."""

    class Meta:
        model = Order
        fields = (
            "pk",
            "delivery_address",
            "promo_code",
            "created_at",
            "user",
            "products",
        )
