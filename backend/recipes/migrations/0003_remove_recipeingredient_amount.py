# Generated by Django 3.2.20 on 2023-07-18 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_rename_units_ingredient_measurement_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipeingredient',
            name='amount',
        ),
    ]
