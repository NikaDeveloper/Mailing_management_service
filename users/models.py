from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django_countries.fields import CountryField


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели User,
    где email является уникальным идентификатором, а username не используется"""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и сохраняет пользователя с email и паролем"""
        if not email:
            raise ValueError("Email должен быть установлен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и сохраняет суперпользователя с email и паролем"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)  # по умолчанию активный

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    avatar = models.ImageField(
        upload_to="users/avatars/", null=True, blank=True, verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=35, null=True, blank=True, verbose_name="Номер телефона"
    )
    country = CountryField(null=True, blank=True, verbose_name="Страна")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

        permissions = [
            ("can_view_all_users", "Может просматривать всех пользователей"),
            ("can_block_user", "Может блокировать пользователей"),
        ]

    def __str__(self):
        return self.email
