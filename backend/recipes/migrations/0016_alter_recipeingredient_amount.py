# Generated by Django 3.2.20 on 2023-07-22 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0015_alter_recipeingredient_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
    ]
