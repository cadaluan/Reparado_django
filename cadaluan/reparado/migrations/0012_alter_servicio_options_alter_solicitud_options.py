# Generated by Django 5.0.1 on 2024-06-17 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reparado', '0011_servicio_tiempo_estimado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicio',
            options={'verbose_name_plural': 'Servicios'},
        ),
        migrations.AlterModelOptions(
            name='solicitud',
            options={'verbose_name_plural': 'Solicitudes'},
        ),
    ]
