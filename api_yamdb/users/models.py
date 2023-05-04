from django.db import models
from django.contrib.auth.models import AbstractUser


ROLE_CHOICES = [
    ("admin", "Администратор"),
    ("moderator", "Модератор"),
    ("user", "Пользователь"),
]


class User(AbstractUser):
    username = models.CharField(
        "username",
        max_length=140,
        unique=True,
    )
    email = models.EmailField(max_length=250)
    first_name = models.CharField("first name", max_length=150, blank=True)
    last_name = models.CharField("last name", max_length=150, blank=True)
    bio = models.TextField(
        "Биография",
        blank=True,
    )
    role = models.TextField(
        "Роль", blank=False, choices=ROLE_CHOICES, default="user"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_moderator(self):
        return self.role == "moderator"

    @property
    def is_user(self):
        return self.role == "user"
