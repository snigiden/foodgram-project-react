# Generated by Django 3.2.20 on 2023-07-19 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_remove_recipeingredient_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='color_code',
            new_name='color',
        ),
    ]
