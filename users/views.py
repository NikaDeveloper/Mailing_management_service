from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import UserProfileForm, UserRegisterForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")


class LoginView(BaseLoginView):
    template_name = "users/login.html"


class LogoutView(BaseLogoutView):
    next_page = reverse_lazy("users:login")


class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class OwnerRequiredMixin:
    """Миксин, который проверяет, что пользователь является владельцем объекта,
    либо является менеджером."""

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Менеджер видит все
        if user.has_perm(
            f"{self.model._meta.app_label}.can_view_all_{self.model._meta.model_name}s"
        ):
            return queryset

        # обычный пользователь видит только свое
        return queryset.filter(owner=user)


class OwnerOrManagerTestMixin(UserPassesTestMixin):
    """Миксин для UpdateView, DeleteView. Проверяет, что юзер - владелец, или менеджер."""

    def test_func(self):
        user = self.request.user
        obj = self.get_object()

        # Суперпользователь всегда может все
        if user.is_superuser:
            return True

        app_label = obj._meta.app_label
        model_name = obj._meta.model_name

        # Проверка прав менеджера
        if model_name == "mailing":
            # Для рассылки менеджеру достаточно права на отключение (can_disable_mailings)
            is_manager = user.has_perm(f"{app_label}.can_disable_mailings")
        else:
            # Для остальных объектов достаточно права на просмотр всех
            is_manager = user.has_perm(f"{app_label}.can_view_all_{model_name}s")

            # Проверка владельца
        is_owner = obj.owner == user

        return is_manager or is_owner
