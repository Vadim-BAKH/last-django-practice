"""Представления пользователей"""

from random import random
from typing import Any, Dict

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import (CreateView, DetailView, FormView, ListView,
                                  UpdateView)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from .forms import AvatarUpdateForm, UserRegisterForm
from .models import Profile
from .serialisers import ProfileSerializer


class ProfileViewSet(ModelViewSet):
    """
    ViewSet для управления профилями пользователей.
    Полный CRUD для сущности пользователя.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "user",
    ]
    filterset_fields = [
        "user",
        "position",
    ]


class AboutMeView(LoginRequiredMixin, FormView):
    """
    Страница редактирования профиля текущего пользователя.
    """

    template_name = "myauth/about-me.html"
    form_class = AvatarUpdateForm
    success_url = reverse_lazy("myauth:about-me")

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Передаёт профиль пользователя в форму."""
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user.profile
        return kwargs

    def form_valid(self, form: Any) -> HttpResponse:
        """Сохраняет изменения профиля."""
        form.save()
        return super().form_valid(form)


class ListProfilesView(ListView):
    """Список всех профилей пользователей."""

    template_name = "myauth/profiles-list.html"
    context_object_name = "profiles"
    queryset = Profile.objects.all()


class ProfileDetailView(DetailView):
    """
    Детальный просмотр профиля пользователя.
    """

    model = Profile
    template_name = "myauth/profile_detail.html"
    context_object_name = "profile"


class ProfileAvatarUpdate(UpdateView, UserPassesTestMixin):
    """
    Обновление аватара профиля (только для сотрудников).
    """

    def test_func(self) -> bool:
        """
        Проверяет, что пользователь является сотрудником.
        """
        return self.request.user.is_staff

    def get_success_url(self) -> str:
        """
        URL для перенаправления после успешного обновления.
        """
        return reverse_lazy("myauth:profile-detail", kwargs={"pk": self.object.pk})

    model = Profile
    form_class = AvatarUpdateForm
    template_name = "myauth/staff-avatar-update.html"
    context_object_name = "profile"


class RegisterUserView(CreateView):
    """
    Регистрация нового пользователя с

    созданием профиля и авторизацией.
    """

    form_class = UserRegisterForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form: Any) -> HttpResponse:
        """
        Создаёт пользователя, профиль и авторизует его.
        """
        response = super().form_valid(form)
        user = self.object
        user.first_name = form.cleaned_data.get("first_name")
        user.last_name = form.cleaned_data.get("last_name")
        user.email = form.cleaned_data.get("email")
        user.save()
        profile = Profile.objects.create(
            user=user,
            position=form.cleaned_data.get("position"),
            agreement_accepted=form.cleaned_data.get("agreement_accepted"),
        )
        avatar = self.request.FILES.get("avatar")
        if avatar:
            profile.avatar = avatar
            profile.save()
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password2")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Выход пользователя и перенаправление на страницу входа.
    """
    logout(request)
    return redirect(reverse("myauth:login"))


@cache_page(20)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")
