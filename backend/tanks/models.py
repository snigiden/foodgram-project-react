from io import StringIO

from django.db import models

from recipes.models import Recipe, RecipeIngredient
from users.models import User


class Favorite(models.Model):
    """Модель избранных рецептов"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
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
        related_name='carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
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

    def create_grocery_queryset(user):
        ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=models.Sum('amount')
        )
        buffer = StringIO()
        for item in ingredients:
            buffer.write(f"{item['ingredient__name']}\t")
            buffer.write(f"{item['amount']}\t")
            buffer.write(f"{item['ingredient__measurement_unit']}\n")
        return buffer
