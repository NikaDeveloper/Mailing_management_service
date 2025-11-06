import logging

from django.core.mail import send_mail
from django.utils import timezone

from config import settings

from .models import Mailing, MailingAttempt

logger = logging.getLogger(__name__)


def _execute_send(mailing):
    """Внутренняя функция: выполняет фактическую отправку писем и записывает попытки"""
    recipients = mailing.recipients.all()
    message = mailing.message

    for recipient in recipients:
        try:
            send_mail(
                subject=message.subject,
                message=message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=mailing,
                status="Успешно",
                server_response="Письмо отправлено",
            )
            logger.info(
                f"Письмо для {recipient.email} (рассылка {mailing.pk}) отправлено."
            )
        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing, status="Не успешно", server_response=str(e)
            )
            logger.error(
                f"Ошибка отправки {recipient.email} (рассылка {mailing.pk}): {e}"
            )

    # Обновляем статус, если это был первый запуск
    if mailing.status == "Создана":
        mailing.status = "Запущена"
        mailing.save()


def send_mailing(mailing):
    """Сервисная функция для отправки одной рассылки (используется планировщиком)"""
    now = timezone.now()
    # Проверка времени должна быть ТОЛЬКО здесь.
    if mailing.first_send_time <= now < mailing.end_time:
        _execute_send(mailing)


def process_mailings():
    """Обрабатывает все активные рассылки"""
    now = timezone.now()
    # Ищем все рассылки, которые должны быть активны
    active_mailings = Mailing.objects.filter(
        status__in=["Создана", "Запущена"], first_send_time__lte=now, end_time__gte=now
    )

    for mailing in active_mailings:
        send_mailing(mailing)

    # Завершаем рассылки, у которых вышло время
    Mailing.objects.filter(status="Запущена", end_time__lt=now).update(
        status="Завершена"
    )
