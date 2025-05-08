"""Модуль с представлениями API."""

from django.contrib.auth.models import Group
from rest_framework.generics import ListCreateAPIView

from .serializers import GroupSerializers

# @api_view(["GET"])
# def hello_world_view(request: Request) -> Response:
#     """
#     Простое API-представление.
#
#     Возвращающее JSON с приветственным сообщением.
#     """
#     return Response({"message": "Hello friends"})


class GroupListView(ListCreateAPIView):
    """
    Класс-представление.

    Для работы со списком групп пользователей.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializers
