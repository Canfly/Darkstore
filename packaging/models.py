# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


# Model "Shipments"
class Shipment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    shipment_date = models.DateField()
    status = models.CharField(max_length=255, choices=[('New', 'New'), ('In progress', 'In progress'), ('Shipped', 'Shipped')])
    channels = models.ManyToManyField('SalesChannel', through='ShipmentChannel')  # ManyToMany relationship with SalesChannel

# Model "Products"
class Product(models.Model):
    #id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    quantity_in_stock = models.IntegerField()
    quantity_at_fbo = models.IntegerField()
    code128 = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255)
    description = models.TextField()

# Model "Sellers"
class Seller(models.Model):
    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=255)
    email = models.EmailField()

# Model "SalesChannel" (formerly CANALS PRODAZH)
class SalesChannel(models.Model):
    name = models.CharField(max_length=255)  # Channel name (e.g., Ozon, Wildberries, Yandex Market)

# Model "ShipmentChannel" (Many-to-Many Relationship Helper)
class ShipmentChannel(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    sales_channel = models.ForeignKey(SalesChannel, on_delete=models.CASCADE)

class User(models.Model):
    name = models.CharField(max_length=255)
    ozon_api_key = models.CharField(max_length=255)
    ozon_client_id = models.CharField(max_length=255)
    wildberries_api_key = models.CharField(max_length=255)
    yandex_market_api_key = models.CharField(max_length=255)
