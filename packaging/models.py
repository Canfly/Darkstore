# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# Model "Shipments"
class Shipment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    shipment_date = models.DateField()
    status = models.CharField(max_length=255,
                              choices=[('New', 'New'), ('In progress', 'In progress'), ('Shipped', 'Shipped')])
    channels = models.ManyToManyField('SalesChannel',
                                      through='ShipmentChannel')  # ManyToMany relationship with SalesChannel


# Model "Products"
class Product(models.Model):
    # id = models.CharField(max_length=255)
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


class CustomUser(AbstractUser):
    INN = models.CharField(max_length=12, unique=True)
    checking_account = models.CharField(max_length=20)
    BIK = models.CharField(max_length=9)
    ozon_client_id = models.CharField(max_length=100, blank=True, null=True)
    ozon_client_key = models.CharField(max_length=100, blank=True, null=True)
    wildberries_api_key = models.CharField(max_length=100, blank=True, null=True)
    yandex_market_api_key = models.CharField(max_length=100, blank=True, null=True)

    # Поле для определения типа пользователя
    USER_TYPES = (
        ('seller', 'Продавец'),
        ('warehouse_worker', 'Работник склада'),
        ('warehouse_manager', 'Менеджер склада'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    # Установка пользовательских имен для обратных отношений
    groups = models.ManyToManyField(
        Group,
        related_name="groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="user_permissions",  # Change the related_name here
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
