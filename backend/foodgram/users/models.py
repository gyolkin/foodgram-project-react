from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import LENGTH_150, LENGTH_254
from .validators import validate_username


class User(AbstractUser):
    """Кастомная пользовательская модель."""
    username = models.CharField(
        max_length=LENGTH_150,
        unique=True,
        validators=[validate_username]
    )
    email = models.EmailField(
        max_length=LENGTH_254,
        unique=True
    )
    password = models.CharField(
        max_length=LENGTH_150
    )
    first_name = models.CharField(
        max_length=LENGTH_150
    )
    last_name = models.CharField(
        max_length=LENGTH_150
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
