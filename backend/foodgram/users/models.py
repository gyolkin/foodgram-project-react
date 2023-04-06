from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная пользовательская модель."""
    username = models.CharField(
        max_length=settings.USER_FIELD_LENGTH,
        unique=True
    )
    email = models.EmailField(
        max_length=settings.USER_LONG_FIELD_LENGTH,
        unique=True
    )
    password = models.CharField(
        max_length=settings.USER_FIELD_LENGTH
    )
    first_name = models.CharField(
        max_length=settings.USER_FIELD_LENGTH
    )
    last_name = models.CharField(
        max_length=settings.USER_FIELD_LENGTH
    )


class Follow(models.Model):
    """Пользовательские подписки на других пользователей."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='no_self_follow'
            ),
        )
