from django.contrib import admin

from tanks.models import Cart, Favorite
from users.models import User

from . import models


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorited')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def favorited(self, obj):
        return obj.favorites_recipe.count()


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


class CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'first_name', 'last_name', 'is_staff')


admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
admin.site.register(models.RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(Cart)
admin.site.register(User)
