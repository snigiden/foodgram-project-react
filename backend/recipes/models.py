from autoslug import AutoSlugField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Содержит модели для рецепта:
# Tag
# Ingredient
# Recipe
# RecipeIngredient


class Tag(models.Model):
    """Модель тегов для рецепта"""
    name = models.TextField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='HEX цвета',
        max_length=7,
        unique=True,
    )
    slug = AutoSlugField(
        verbose_name='Слаг',
        unique=True,
        populate_from='name',
        editable=False,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов и меры их веса"""
    name = models.TextField(
        verbose_name='Название',
        max_length=200,
    )
    measurement_unit = models.TextField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='uploads/recipes',
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=400,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи рецепта с ингредиентами"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиенты из рецепта'
        verbose_name_plural = 'Ингредиенты из рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination',
            )
        ]
