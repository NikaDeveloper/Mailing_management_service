from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailing.models import Mailing, Message, Recipient
from users.models import User


class Command(BaseCommand):
    help = 'Создает группу "Менеджеры" и выдает ей права'

    def handle(self, *args, **options):
        manager_group, created = Group.objects.get_or_create(name="Менеджеры")
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана.'))

        # Получаем нужные permissions
        perms_codenames = [
            "can_view_all_mailings",
            "can_disable_mailings",
            "can_view_all_recipients",
            "can_view_all_messages",
            "can_view_all_users",
            "can_block_user",
        ]

        # Собираем все Content Types
        content_types = ContentType.objects.get_for_models(
            Mailing, Recipient, Message, User
        )

        permissions = []
        for content_type in content_types.values():
            perms = Permission.objects.filter(
                content_type=content_type, codename__in=perms_codenames
            )
            permissions.extend(perms)

        manager_group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Права для группы "Менеджеры" настроены.'))
