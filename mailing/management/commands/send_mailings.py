from django.core.management.base import BaseCommand

from mailing.services import process_mailings


class Command(BaseCommand):
    help = "Отправляет активные рассылки"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Начинаю обработку рассылок..."))
        process_mailings()
        self.stdout.write(self.style.SUCCESS("Обработка рассылок завершена."))
