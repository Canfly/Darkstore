# Generated by Django 5.0.3 on 2024-03-27 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packaging', '0023_remove_shipment_product_shipment_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shipment',
            old_name='product',
            new_name='products',
        ),
        migrations.AlterField(
            model_name='shipment',
            name='shipment_date',
            field=models.DateTimeField(),
        ),
    ]
