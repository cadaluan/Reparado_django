# Generated by Django 5.0.1 on 2024-09-21 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reparado', '0020_alter_compra_options_alter_factura_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='compra',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compra',
            name='estado',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'Creado'), (2, 'Pagada'), (3, 'Enviada'), (4, 'Cancelada')], default=1),
        ),
    ]
