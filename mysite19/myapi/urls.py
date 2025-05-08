"""URL-конфигурация приложения 'myapi'."""

from django.urls import path

from .views import GroupListView

app_name = "myapi"

urlpatterns = [
    # path("hello/", hello_world_view, name="hello"),
    path("groups/", GroupListView.as_view(), name="groups"),
]
