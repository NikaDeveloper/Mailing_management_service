import logging
import time

from django.core.management.base import BaseCommand

from mailing.scheduler import start_scheduler

logger = logging.getLogger("scheduler")


class Command(BaseCommand):
    help = "Запускает планировщик APScheduler в отдельном процессе."

    def handle(self, *args, **options):
        # 1. Запуск планировщика
        start_scheduler()

        self.stdout.write(self.style.SUCCESS("Планировщик рассылок запущен успешно."))
        self.stdout.write("Для остановки нажмите CTRL+C.")

        # 2. Не даем процессу завершиться
        try:
            # Цикл, чтобы процесс оставался активным в фоне
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("\nПланировщик остановлен пользователем.")
