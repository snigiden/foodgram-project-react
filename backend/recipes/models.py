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
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        unique=True,
    )
    slug = AutoSlugField(
        unique=True,
        populate_from='name',
        editable=False,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов и меры веса"""
    name = models.TextField(
        max_length=200,
    )
    measurement_unit = models.TextField(
        max_length=200,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='uploads/recipes',
    )
    text = models.TextField(
        max_length=400,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
    )
    cooking_time = models.PositiveIntegerField()
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи рецепта с ингредиентами"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    amount = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination',
            )
        ]
