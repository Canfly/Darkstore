import requests
from .models import  Product

URL_API = "https://api.moysklad.ru/api/remap/1.2/entity/product"

def parse_product_data(response):
    data = response.json()
    return {
        "name": data["name"],
        "sku": data["artikul"],
        "quantity_in_stock": data["quantity"],
        "price": data["price"],
        "category": data["category"]["name"],
        "description": data["description"],
    }

def update_product_from_api(product_id, response):
    """Updates the product with the given ID from the API response."""
    # измените "id" на правильный ключ для идентификатора продукта из API
    #product_id = product["code"]  

    product = Product.objects.get(pk=product_id)
    data = parse_product_data(response)
    for field, value in data.items():
        setattr(product, field, value)
    product.save()