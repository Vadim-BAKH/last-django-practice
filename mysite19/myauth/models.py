"""Модели пользователей"""

from django.contrib.auth.models import User
from django.db import models


def profile_avatars_directory_path(instance: "Profile", filename: str) -> str:
    """
    Формирует путь для сохранения аватара пользователя.
    """
    return f"files/images_{instance.pk}/avatar/{filename}"


class Profile(models.Model):
    """
    Модель профиля пользователя.

    Attributes:
        user (User): Связанный пользователь.
        position (str): Должность пользователя.
        agreement_accepted (bool): Принят ли пользователь соглашение.
        avatar (ImageField): Аватар пользователя.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=False, null=False)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, upload_to=profile_avatars_directory_path)
