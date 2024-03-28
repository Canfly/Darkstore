import requests
from .models import Product, CustomUser, MarketPlaceArticle, Shipment
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
    if 'barcodes' in list(response.keys()):
        for code in response['barcodes']:
            if 'code128' in list(code.keys()):
                code = MarketPlaceArticle(code=code['code128'])
                code.save()
                product.marketplaces_articles.add(code)
    product.save()


def update_stocks_from_api(article, quantity):
    product = Product.objects.filter(article=article).first()
    if product:
        product.quantity_in_stock = quantity
    product.save()






def add_shipment_from_api(user, data):
    exists = Shipment.objects.filter(marketplace_id=data['marketplace_id'])
    if not exists:
        shipment = Shipment()
        for field, value in list(data.items())[:-1]:
            setattr(shipment, field, value)
        products = Product.objects.filter(owner=user)
        shipment.seller = user
        shipment.save()
        for shipment_product in data['products']:
            for db_product in products:
                for article in list(db_product.marketplaces_articles.all()):
                    if shipment_product['offer_id'] == article.code:
                        shipment.products.add(db_product)
                        break
    else:
        shipment = exists[0]
    if data['status'] == 'awaiting_deliver':
        shipment.pdf = f'package-labels/output_{data["marketplace_id"]}'
    shipment.save()





