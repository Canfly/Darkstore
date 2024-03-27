import requests
from .models import Product, CustomUser
from django.shortcuts import get_object_or_404

URL_API = "https://api.moysklad.ru/api/remap/1.2/entity/product"


def parse_product_data(response):
    data = response
    return {
        "name": data["name"],
        "sku": data["code"],
        "quantity_at_fbo": 0,
        "quantity_in_stock": 0,
        "category": data["pathName"],
        "description": data["description"] if "description" in list(data.keys()) else "",
        "article": data["article"],
        "moysklad_id": data["id"]
    }


def update_product_from_api(product_id, response):
    """Updates the product with the given ID from the API response."""
    # измените "id" на правильный ключ для идентификатора продукта из API
    # product_id = product["code"]
    product = Product.objects.filter(article=product_id).first()
    data = parse_product_data(response)
    q = product.quantity_in_stock
    if product:
        product.quantity_in_stock = product.quantity_in_stock
    else:
        product = Product()
    for field, value in data.items():
        setattr(product, field, value)
    product.quantity_in_stock = q
    owners = CustomUser.objects.filter(INN=product.article.split(":")[0])
    if owners:
        product.owner.add(owners[0])
    print(product['barcodes'])
    product.save()


def update_stocks_from_api(article, quantity):
    product = Product.objects.filter(article=article).first()
    if product:
        product.quantity_in_stock = quantity
    product.save()
