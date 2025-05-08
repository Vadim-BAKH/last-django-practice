"""Модуль сериализаторов."""

from django.contrib.auth.models import Group
from rest_framework.serializers import ModelSerializer


class GroupSerializers(ModelSerializer):
    """
    Класс GroupSerializers.

    Преобразует объекты Group в формат JSON и обратно.
    """

    class Meta:
        model = Group
        fields = (
            "pk",
            "name",
        )
