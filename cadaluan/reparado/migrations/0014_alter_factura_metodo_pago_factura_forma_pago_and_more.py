# Generated by Django 5.0.1 on 2024-07-07 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reparado', '0013_delete_auditoria_remove_facturapago_factura_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='factura',
            name='metodo_pago',
            field=models.CharField(choices=[('EFECTIVO', 'Efectivo'), ('TARJETA_DEBITO', 'Tarjeta de débito'), ('TARJETA_CREDITO', 'Tarjeta de crédito'), ('TRANSFERENCIA_BANCARIA', 'Transferencia bancaria'), ('PAYPAL', 'PayPal'), ('CHEQUE', 'Cheque')], default='EFECTIVO', max_length=50),
        ),
        migrations.AddField(
            model_name='factura',
            name='forma_pago',
            field=models.CharField(choices=[('CONTADO', 'Pago al contado'), ('CREDITO', 'Pago mediante crédito'), ('DEBITO_AUTOMATICO', 'Pago mediante débito automático'), ('TRANSFERENCIA_BANCARIA', 'Pago mediante transferencia bancaria'), ('TARJETA_CREDITO', 'Pago con tarjeta de crédito'), ('TARJETA_DEBITO', 'Pago con tarjeta de débito')], default='CONTADO', max_length=50),
        ),
        migrations.DeleteModel(
            name='MetodoPago',
        ),
    ]
