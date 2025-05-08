"""
URL-конфигурация приложения myauth.

Определяет маршруты для API профилей,

аутентификации и управления пользователями.
"""

from django.contrib.auth.views import LoginView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AboutMeView, ListProfilesView, ProfileAvatarUpdate,
                    ProfileDetailView, ProfileViewSet, RegisterUserView,
                    get_cookie_view, logout_view)

app_name = "myauth"

routers = DefaultRouter()
routers.register("profiles", ProfileViewSet)

urlpatterns = [
    path("api/", include(routers.urls)),
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", logout_view, name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterUserView.as_view(), name="register"),
    path("cookie/get/", get_cookie_view, name="cookie_get"),
    path("profiles/", ListProfilesView.as_view(), name="profiles"),
    path("profiles/<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
    path(
        "profile/avatar/update/<int:pk>/",
        ProfileAvatarUpdate.as_view(),
        name="staff-avatar-update",
    ),
]
