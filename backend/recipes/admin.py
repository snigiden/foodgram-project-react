from django.contrib import admin
from . import models


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    empty_value_display = '-пусто-'

class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')
    empty_value_display = '-пусто-'


admin.site.register(models.Recipe)
admin.site.register(models.Tag)