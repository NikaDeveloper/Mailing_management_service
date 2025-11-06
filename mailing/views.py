from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from users.views import OwnerOrManagerTestMixin, OwnerRequiredMixin

from .forms import MailingForm
from .models import Mailing, MailingAttempt, Message, Recipient
from .services import _execute_send


class HomePageView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Если пользователь неаутентифицирован или является менеджером / суперпользователем,
        # используем глобальную (кэшированную) статистику
        if (
            not user.is_authenticated
            or user.is_superuser
            or user.has_perm("mailing.can_view_all_mailings")
        ):
            cached_data = cache.get("home_page_stats")

            if cached_data is None:
                # Если в кэше нет, считаем и кладем в кэш
                cached_data = {
                    "total_mailings": Mailing.objects.count(),
                    "active_mailings": Mailing.objects.filter(
                        status="Запущена"
                    ).count(),
                    # Используем distinct() для уникальных клиентов
                    "unique_recipients": Recipient.objects.distinct().count(),
                }
                cache.set("home_page_stats", cached_data, 60 * 15)  # кэш на 15 минут

            context.update(cached_data)
        # сли это обычный аутентифицир. пользователь - показываем его личную статистику
        else:
            context.update(
                {
                    "total_mailings": Mailing.objects.filter(owner=user).count(),
                    "active_mailings": Mailing.objects.filter(
                        owner=user, status="Запущена"
                    ).count(),
                    # количество уникальных клиентов, созданных этим пользователем
                    "unique_recipients": Recipient.objects.filter(owner=user)
                    .distinct()
                    .count(),
                }
            )

        return context


class MailingListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"


class MailingDetailView(LoginRequiredMixin, OwnerOrManagerTestMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    template_name = "mailing/mailing_form.html"
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        self.object = form.save(commit=False)  # commit=False для привязки владельца
        self.object.owner = self.request.user
        self.object.save()
        form.save_m2m()  # для сохранения ManyToMany для recipients
        return redirect(self.success_url)


class MailingUpdateView(LoginRequiredMixin, OwnerOrManagerTestMixin, UpdateView):
    model = Mailing
    template_name = "mailing/mailing_form.html"
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(LoginRequiredMixin, OwnerOrManagerTestMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")


class MessageListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"


class MessageDetailView(LoginRequiredMixin, OwnerOrManagerTestMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ("subject", "body")
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):

        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerOrManagerTestMixin, UpdateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ("subject", "body")
    success_url = reverse_lazy("mailing:message_list")


class MessageDeleteView(LoginRequiredMixin, OwnerOrManagerTestMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


class RecipientListView(LoginRequiredMixin, OwnerRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"


class RecipientDetailView(LoginRequiredMixin, OwnerOrManagerTestMixin, DetailView):
    model = Recipient
    template_name = "mailing/recipient_detail.html"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = "mailing/recipient_form.html"
    fields = ("email", "full_name", "comment")
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):

        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerOrManagerTestMixin, UpdateView):
    model = Recipient
    template_name = "mailing/recipient_form.html"
    fields = ("email", "full_name", "comment")
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientDeleteView(LoginRequiredMixin, OwnerOrManagerTestMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/attempt_list.html"

    def get_queryset(self):
        # Отчеты только по своим рассылкам (или все для менеджера)
        user = self.request.user
        if user.has_perm("mailing.can_view_all_mailings"):
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=user)


def manual_send(request, pk):
    if not request.user.is_authenticated:
        return redirect("users:login")

    mailing = get_object_or_404(Mailing, pk=pk)
    user = request.user

    # Суперпользователь всегда имеет доступ
    if user.is_superuser:
        is_allowed = True
    else:
        # Проверка прав: Владелец ИЛИ Менеджер (can_disable_mailings)
        is_owner = mailing.owner == user
        can_disable = user.has_perm("mailing.can_disable_mailings")

        # Менеджер, даже если он не владелец, должен иметь право отключения
        is_allowed = is_owner or can_disable

    if not is_allowed:
        raise Http404

    try:
        _execute_send(mailing)
        messages.success(request, "Рассылка отправлена вручную.")
    except Exception as e:
        messages.error(request, f"Ошибка при ручной отправке: {e}")

    return redirect("mailing:mailing_detail", pk=pk)
