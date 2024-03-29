# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, User


class CustomUser(AbstractUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    INN = models.CharField(max_length=12, unique=True)
    checking_account = models.CharField(max_length=20)
    BIK = models.CharField(max_length=9)
    ozon_client_id = models.CharField(max_length=100, blank=True, null=True)
    ozon_client_key = models.CharField(max_length=100, blank=True, null=True)
    wildberries_api_key = models.CharField(max_length=100, blank=True, null=True)
    yandex_market_api_key = models.CharField(max_length=100, blank=True, null=True)
    moysklad_id = models.CharField(max_length=100, blank=True, null=True)
    moysklad_user = models.CharField(max_length=100, blank=True, null=True)
    moysklad_pass = models.CharField(max_length=100, blank=True, null=True)

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

    # def __str__(self):
    #     return self.user.


# Model "Shipments"
class Shipment(models.Model):
    marketplace_id = models.CharField(max_length=255, blank=True, null=True)
    moysklad_id = models.CharField(max_length=255, blank=True, null=True)
    products = models.ManyToManyField('Product')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shipment_date = models.DateTimeField()
    status = models.CharField(max_length=255,
                              choices=[('New', 'New'), ('In progress', 'In progress'), ('Shipped', 'Shipped')])
    channels = models.ManyToManyField('SalesChannel',
                                      through='ShipmentChannel')  # ManyToMany relationship with SalesChannel
    pdf = models.CharField(max_length=255, blank=True, null=True)
    minipdf = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    products_codes128 = models.TextField()

    def __str__(self):
        return str(self.marketplace_id) + ' '+ str(self.seller.user.first_name) + ' ' + str(self.seller.user.last_name)


# Model MarketPlaceArticle
class MarketPlaceArticle(models.Model):
    MARKETPLACES_TYPES = (
        ('OZON', 'OZON'),
        ('Wildeberries', 'Wildberries'),
        ('YandexMarket', 'Yandex Market'),
    )
    marketplace_type = models.CharField(max_length=100, choices=MARKETPLACES_TYPES, blank=True, null=True)
    code = models.CharField(max_length=255)

    def __str__(self):
        return str(self.marketplace_type) + ' ' + str(self.code) if self.marketplace_type else \
            str(self.code)


# Model "Products"
class Product(models.Model):
    # id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    quantity_in_stock = models.IntegerField(blank=True, null=True)
    quantity_at_fbo = models.IntegerField(blank=True, null=True)
    code128 = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    article = models.CharField(max_length=255, blank=True, null=True)
    moysklad_id = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ManyToManyField(CustomUser)
    marketplaces_articles = models.ManyToManyField(MarketPlaceArticle)

    def __str__(self):
        return str(self.name)


# Model "SalesChannel" (formerly CANALS PRODAZH)
class SalesChannel(models.Model):
    name = models.CharField(max_length=255)  # Channel name (e.g., Ozon, Wildberries, Yandex Market)

    def __str__(self):
        return str(self.name)


# Model "ShipmentChannel" (Many-to-Many Relationship Helper)
class ShipmentChannel(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    sales_channel = models.ForeignKey(SalesChannel, on_delete=models.CASCADE)
