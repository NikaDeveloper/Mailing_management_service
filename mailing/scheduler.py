import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore, register_events

from mailing.services import process_mailings

logger = logging.getLogger(__name__)


def mailing_job():
    print("Запуск задачи рассылки...")  # для отладки
    process_mailings()
    print("Задача рассылки завершена.")


def start_scheduler():
    """Главная функция запуска планировщика"""
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        mailing_job,
        trigger="interval",  # тип триггера интервал
        minutes=1,  # интервал 1 минута
        id="mailing_job",  # уникальный ID задачи
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Задача рассылки добавлена в планировщик.")

    try:
        logger.info("Запуск планировщика...")
        register_events(scheduler)
        scheduler.start()
    except Exception as e:
        logger.error(f"Ошибка запуска планировщика: {e}")
        scheduler.shutdown()
