"""Формы для действий с профилем пользователя"""

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import (BooleanField, CharField, EmailField, ImageField,
                          ModelForm)

from .models import Profile


class UserRegisterForm(UserCreationForm):
    """
    Форма регистрации пользователя с дополнительными полями.
    """

    class Meta:
        model = User
        fields = (
            "username",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "email",
        )

    first_name = CharField(max_length=50, required=False, label="First name")
    last_name = CharField(max_length=50, required=False, label="Last name")
    email = EmailField(required=True, label="Email")
    position = CharField(max_length=100, required=True)
    avatar = ImageField(required=False)
    agreement_accepted = BooleanField(required=True)


class AvatarUpdateForm(ModelForm):
    """Форма для обновления аватара пользователя."""

    class Meta:
        model = Profile
        fields = ("avatar",)
