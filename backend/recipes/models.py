from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField

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
    color_code = models.CharField(
        max_length=7,
        unique=True,
    )
    slug = AutoSlugField(
        unique=True,
        populate_from='name',
        editable=True,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов и меры веса"""
    name = models.TextField(
        max_length=200,
    )
    units = models.TextField(
        max_length=200,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='uploads/recipes',
    )
    description = models.TextField(
        max_length=400,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    cook_time = models.PositiveIntegerField
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
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        max_length=200,
    )
