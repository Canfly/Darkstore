# Generated by Django 5.0.3 on 2024-03-26 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packaging', '0009_alter_product_quantity_at_fbo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
