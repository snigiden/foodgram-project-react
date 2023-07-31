from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[а-яА-ЯёЁa-zA-Z0-9]+$',
                message='Имя пользователя может содержать только буквы и цифры'
            ),
        ],
    )
    email = models.EmailField(
        max_length=200,
        unique=True,
    )
    first_name = models.TextField(
        max_length=100,
    )
    last_name = models.TextField(
        max_length=100,
    )

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_sub',
            )
        ]
