# Generated by Django 3.2.20 on 2023-07-22 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20230722_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
