# Generated by Django 5.0.3 on 2024-03-26 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packaging', '0010_alter_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='moysklad_id',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
