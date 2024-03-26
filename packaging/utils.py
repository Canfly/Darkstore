import requests
from .models import Product
from django.shortcuts import get_object_or_404

URL_API = "https://api.moysklad.ru/api/remap/1.2/entity/product"


def parse_product_data(response):
    data = response
    return {
        "name": data["name"],
        "sku": data["code"],
        "quantity": 0,
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
    if product:
        product['quantity'] = product.quantity_in_stock
    else:
        product = Product()
    for field, value in data.items():
        setattr(product, field, value)
    product.save()


def update_stocks_from_api(article, quantity):
    product = Product.objects.filter(article=article).first()
    if product:
        product.quantity_in_stock = quantity
    product.save()
