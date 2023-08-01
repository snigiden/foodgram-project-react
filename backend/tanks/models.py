from django.db import models

from recipes.models import Recipe
from users.models import User


class Favorite(models.Model):
    """Модель избранных рецептов"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite',
            )
        ]


class Cart(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_cart',
            )
        ]
