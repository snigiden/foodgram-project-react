# Generated by Django 3.2.20 on 2023-07-22 23:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_recipe_ingredient_recipe'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Recipe_ingredient',
            new_name='RecipeIngredient',
        ),
    ]
