import requests
from .models import Product, CustomUser, MarketPlaceArticle, Shipment
from django.shortcuts import get_object_or_404
import base64
import barcode
import cairosvg

URL_API = "https://api.moysklad.ru/api/remap/1.2/entity/product"


def get_access_token():
    LOGIN = "sklad@fillrufill"
    PASSWORD = "FillRu2024Password"

    return f"Basic: {base64.b64encode(f'{LOGIN}:{PASSWORD}'.encode('ascii')).decode('ascii')}"


def add_shipment_to_payload(payload, shipment):
    payload["moment"] = str(shipment.shipment_date.replace(tzinfo=None))
    for product in shipment.products.all():
        product_payload = {
            "quantity": 1,
            "price": 0,
            "assortment": {
                "meta": {
                    "href": f"https://api.moysklad.ru/api/remap/1.2/entity/product/{product.moysklad_id}",
                    "metadataHref": "https://api.moysklad.ru/api/remap/1.2/entity/product/metadata",
                    "type": "product",
                    "mediaType": "application/json",
                    "uuidHref": f"https://online.moysklad.ru/app/#product/edit?id={product.moysklad_id}"}}}
        in_payload = False
        for iter_product in payload["positions"]:
            if product_payload["assortment"] == iter_product["assortment"]:
                iter_product["quantity"] += 1
                in_payload = True
                break
        if not in_payload:
            payload["positions"].append(product_payload)
    if shipment.pdf:
        with open(shipment.pdf, "rb") as pdf_file:
            pdf_content = pdf_file.read()
        # Кодируем содержимое PDF-файла в формат Base64
        pdf_base64 = base64.b64encode(pdf_content).decode()

        # Готовим JSON-полезную нагрузку
        payload['files'].append(
            {"filename": f'pdf-{shipment.marketplace_id}.pdf',  # Извлекаем имя файла из пути
             "content": pdf_base64})
    skus = shipment.products_skus.split('\n')[:-1]
    codes = shipment.products_codes128.split('\n')[:-1]
    print(skus, codes)
    for i in range(len(skus)):
        with open(f'minipdfs/OZN{skus[i]}.pdf', "rb") as pdf_file:
            pdf_content = pdf_file.read()
        # Кодируем содержимое PDF-файла в формат Base64
        pdf_base64 = base64.b64encode(pdf_content).decode()
        file_payload = {"filename": f'minipdf-{codes[i]}.pdf',  # Извлекаем имя файла из пути
                        "content": pdf_base64}

        if file_payload not in payload["files"]:
            payload["files"].append(file_payload)


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
    moiseeva = CustomUser.objects.filter(INN="622400183009").first()
    alexeeva = CustomUser.objects.filter(INN="622402110214").first()
    if owners:
        product.owner.add(owners[0])
    if product.article.split(":")[0] in ("622400183009", "622402110214"):
        product.owner.add(alexeeva)
        product.owner.add(moiseeva)
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
    else:
        shipment = exists[0]
    for field, value in list(data.items())[:-1]:
        setattr(shipment, field, value)
    products = Product.objects.filter(owner=user)
    shipment.seller = user
    shipment.save()
    shipment.products_codes128 = ''
    shipment.products_skus = ''
    for shipment_product in data['products']:
        for db_product in products:
            for article in list(db_product.marketplaces_articles.all()):
                if shipment_product['offer_id'] == article.code:
                    shipment.products.add(db_product)
                    shipment.products_codes128 += article.code + '\n'
                    shipment.products_skus += str(shipment_product["sku"]) + '\n'
                    generate_mini_pdf(str(shipment_product["sku"]), shipment_product['offer_id'],
                                      shipment_product['offer_id'])
                    break
    if data['status'] == 'awaiting_deliver':
        shipment.pdf = f'package-labels/pdf_{data["marketplace_id"]}.pdf'
    shipment.save()


def attach_pdfs_to_shipment(shipment_id, files):
    # Готовим заголовки
    headers = {
        "Authorization": get_access_token()
    }

    for i in range(0, len(files), 10):
        if i + 10 <= len(files):
            # Отправляем POST-запрос к API для прикрепления PDF-файла к отгрузке
            response = requests.post(f"https://api.moysklad.ru/api/remap/1.2/entity/demand/{shipment_id}/files",
                                     headers=headers,
                                     json=files[i: i + 10])
        else:
            response = requests.post(f"https://api.moysklad.ru/api/remap/1.2/entity/demand/{shipment_id}/files",
                                     headers=headers,
                                     json=files[i: len(files)])

        # Проверяем статус ответа
        if response.status_code == 200:
            print(f"PDF-файл успешно прикреплен к отгрузке {shipment_id}.")
        else:
            print(
                f"Не удалось прикрепить PDF-файл к отгрузке {shipment_id}. Статус код: {response.status_code}, Ответ: {response.text}")


def generate_mini_pdf(code, text, name):
    marketplace_code = 'OZN' + code
    marketplace_code = barcode.codex.Code128(marketplace_code)
    marketplace_code = marketplace_code.save('svg/OZN' + code, {'module_height': 15, 'font_size': 5,'text_distance':3},
                                             text='OZN' + code)
    cairosvg.svg2pdf(url=f'svg/OZN{code}.svg', write_to=f'minipdfs/OZN{code}.pdf', output_width=151, output_height=114)
