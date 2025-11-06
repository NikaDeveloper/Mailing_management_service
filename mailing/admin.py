from django.contrib import admin

from .models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Класс регистрации получателей"""

    list_display = ("email", "full_name", "owner")
    search_fields = ("email", "full_name")
    list_filter = ("owner",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Класс регистрации сообщений"""

    list_display = ("subject", "owner")
    search_fields = ("subject",)
    list_filter = ("owner",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Класс регистрации рассылок"""

    list_display = ("id", "status", "first_send_time", "end_time", "owner")
    list_filter = ("status", "owner")
    # Дополнительно: чтобы видеть, какие получатели привязаны
    filter_horizontal = ("recipients",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Класс регистрации попыток рассыоки"""

    list_display = ("id", "mailing", "attempt_time", "status")
    list_filter = ("status", "mailing")
    readonly_fields = ("attempt_time",)
