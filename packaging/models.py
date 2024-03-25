from django.db import models


# Model "Shipments"
class Shipment(models.Model):
    main_sticker = models.CharField(max_length=255)
    small_sticker = models.CharField(max_length=255)
    code128 = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    shipment_date = models.DateField()
    status = models.CharField(max_length=255,
                              choices=[('New', 'New'), ('In progress', 'In progress'), ('Shipped', 'Shipped')])


# Model "Products"
class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    quantity_in_stock = models.IntegerField()
    quantity_at_fbo = models.IntegerField()


# Model "Sellers"
class Seller(models.Model):
    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=255)
    email = models.EmailField()


class User(models.Model):
    name = models.CharField(max_length=255)
    ozon_api_key = models.CharField(max_length=255)
    ozon_client_id = models.CharField(max_length=255)
    wildberries_api_key = models.CharField(max_length=255)
    yandex_market_api_key = models.CharField(max_length=255)
