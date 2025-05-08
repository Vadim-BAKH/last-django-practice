"""
Сериализатор для преобразования данных профиля

пользователя в формат JSON и обратно.
"""

from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя.
    """

    class Meta:
        model = Profile
        fields = (
            "user",
            "position",
            "agreement_accepted",
            "avatar",
        )
