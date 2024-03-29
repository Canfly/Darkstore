import requests
from .models import Product, CustomUser, MarketPlaceArticle, Shipment
from django.shortcuts import get_object_or_404
import base64


URL_API = "https://api.moysklad.ru/api/remap/1.2/entity/product"


def add_shipment_to_payload(payload, shipment):
    payload["moment"] = str(shipment.shipment_date.replace(tzinfo=None))
    for product in shipment.products.all():
        payload["positions"].append({
            "quantity": 1,
            "price": 0,
            "assortment": {
                "meta": {
                    "href": f"https://api.moysklad.ru/api/remap/1.2/entity/product/{product.moysklad_id}",
                    "metadataHref": "https://api.moysklad.ru/api/remap/1.2/entity/product/metadata",
                    "type": "product",
                    "mediaType": "application/json",
                    "uuidHref": f"https://online.moysklad.ru/app/#product/edit?id={product.moysklad_id}"}}})
    if shipment.pdf:
        with open(shipment.pdf, "rb") as pdf_file:
            pdf_content = pdf_file.read()
        # Кодируем содержимое PDF-файла в формат Base64
        pdf_base64 = base64.b64encode(pdf_content).decode()

        # Готовим JSON-полезную нагрузку
        payload['files'].append(
            {"filename": 'big_pdf.pdf',  # Извлекаем имя файла из пути
             "content": pdf_base64})


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
    exists = False
    product = Product.objects.filter(article=product_id).first()
    data = parse_product_data(response)
    if product:
        q = product.quantity_in_stock
        exists = True
    else:
        product = Product()
    for field, value in data.items():
        setattr(product, field, value)
    if exists:
        product.quantity_in_stock = q
    product.save()
    owners = CustomUser.objects.filter(INN=product.article.split(":")[0])
    if owners:
        product.owner.add(owners[0])
    if 'barcodes' in list(response.keys()):
        for code in response['barcodes']:
            if 'code128' in list(code.keys()):
                article = MarketPlaceArticle.objects.filter(marketplace_type='OZON', code=code['code128'])
                if not article:
                    article = MarketPlaceArticle(marketplace_type='OZON', code=code['code128'])
                else:
                    article = article[0]
                article.save()
                product.marketplaces_articles.add(article)
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
                        shipment.products_codes128 += article.code + '\n'
                        break
    else:
        shipment = exists[0]
    if data['status'] == 'awaiting_deliver':
        shipment.pdf = f'package-labels/output_{data["marketplace_id"]}.pdf'
    shipment.save()
