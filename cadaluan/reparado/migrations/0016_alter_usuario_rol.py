# Generated by Django 5.0.1 on 2024-09-17 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reparado', '0015_alter_servicio_options_alter_solicitud_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(blank=True, choices=[('ADMIN', 'Administrador'), ('TEC', 'Técnico'), ('USU', 'Usuario')], default='USU', max_length=5, null=True),
        ),
    ]
