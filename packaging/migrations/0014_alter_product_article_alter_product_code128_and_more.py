# Generated by Django 5.0.3 on 2024-03-26 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packaging', '0013_customuser_moysklad_id_product_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='article',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='code128',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='moysklad_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
