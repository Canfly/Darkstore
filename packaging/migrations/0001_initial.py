# Generated by Django 5.0.3 on 2024-03-25 10:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('sku', models.CharField(max_length=255)),
                ('quantity_in_stock', models.IntegerField()),
                ('quantity_at_fbo', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tax_id', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_sticker', models.CharField(max_length=255)),
                ('small_sticker', models.CharField(max_length=255)),
                ('code128', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('shipment_date', models.DateField()),
                ('status', models.CharField(choices=[('New', 'New'), ('In progress', 'In progress'), ('Shipped', 'Shipped')], max_length=255)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='packaging.product')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='packaging.seller')),
            ],
        ),
    ]
