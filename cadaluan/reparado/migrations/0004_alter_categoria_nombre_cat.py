# Generated by Django 5.0.1 on 2024-05-28 22:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reparado', '0003_alter_usuario_password_alter_usuario_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='nombre_cat',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[a-zA-Z\\s]*$', 'El nombre solo puede contener letras y espacios.')]),
        ),
    ]
