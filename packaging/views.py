from datetime import datetime, timedelta

from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests
from .models import Shipment, Product, CustomUser
from .utils import update_product_from_api, update_stocks_from_api, add_shipment_from_api, \
    add_shipment_to_payload, attach_pdfs_to_shipment
import json

import base64

from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, RegisterForm


def get_pdf(posting_number, user):
    url = "https://api-seller.ozon.ru/v2/posting/fbs/package-label"

    try:
        headers = {
            "Client-Id": user.ozon_client_id,
            "Api-Key": user.ozon_client_key
        }

        payload = {
            "posting_number": [posting_number]
        }

        response = requests.post(url, headers=headers, json=payload)

        response.raise_for_status()

        with open(f"package-labels/pdf_{posting_number}.pdf", "wb") as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        return None


def home(request):
    # добавить проверку на авторизацию
    owners = CustomUser.objects.filter(user=request.user)
    return render(request, 'products.html', {'owners': owners})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {"form": form})


def get_access_token():
    LOGIN = "sklad@fillrufill"
    PASSWORD = "FillRu2024Password"

    return f"Basic: {base64.b64encode(f'{LOGIN}:{PASSWORD}'.encode('ascii')).decode('ascii')}"


def get_adiom_access_token():
    LOGIN = "admin@adiom1"
    PASSWORD = "e13188947b"

    return f"Basic: {base64.b64encode(f'{LOGIN}:{PASSWORD}'.encode('ascii')).decode('ascii')}"


def sync_products(request, celery=False):
    """Syncs products from MoySklad."""
    LOGIN = "sklad@fillrufill"
    PASSWORD = "FillRu2024Password"
    URL_API = "https://api.moysklad.ru/api/remap/1.2/entity/product"
    headers = {"Authorization": get_access_token()}
    f = False
    try:
        f = request.method == "POST"
    except AttributeError:
        f = True
    if f or celery == True:
        response = requests.get(URL_API, headers=headers)
        # print(response.json())
        with open('products.json', 'w') as file:
            json.dump(response.json(), file, indent=2)
        if response.status_code == 200:
            products = []
            for product in response.json()["rows"]:
                product_id = update_product_from_api(product["article"], product)
                products.append({"sku": product_id, "name": product["name"]})
            return JsonResponse(products, safe=False)
        else:
            return HttpResponse(status=500)

    return render(request, "sync_products.html")


def sync_stocks(request=None, celery=False):
    """Syncs products from MoySklad."""
    LOGIN = "sklad@fillrufill"
    PASSWORD = "FillRu2024Password"
    URL_API = "https://api.moysklad.ru/api/remap/1.2/report/stock/all"
    headers = {"Authorization": get_access_token()}
    response = requests.get(URL_API, headers=headers)
    f = False
    try:
        f = request.method == "POST"
    except AttributeError:
        f = True
    if f or celery == True:
        response = requests.get(URL_API, headers=headers)
        # print(response.json())
        if response.status_code == 200:
            products = []
            for product in response.json()["rows"]:
                product_id = update_stocks_from_api(product["article"], product["quantity"])
                products.append({"sku": product_id, "name": product["name"]})
            return JsonResponse(products, safe=False)
        else:
            return HttpResponse(status=500)

    return render(request, "sync_stocks.html")


def update_shipments(request):
    if request.method == "POST":

        user = CustomUser.objects.filter(user=request.user)
        if user:
            user = user[0]
            if user.ozon_client_id and user.ozon_client_key:
                url = "https://api-seller.ozon.ru/v3/posting/fbs/unfulfilled/list"

                try:
                    # Загрузка переменных из файла .env

                    headers = {
                        "Client-Id": user.ozon_client_id,
                        "Api-Key": user.ozon_client_key
                    }

                    date_from = datetime.utcnow() - timedelta(hours=24)
                    date_to = datetime.utcnow() + timedelta(hours=48)

                    payload = {
                        "dir": "ASC",
                        "filter": {
                            "cutoff_from": date_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "cutoff_to": date_to.strftime("%Y-%m-%dT%H:%M:%SZ")
                        },
                        "limit": 100,
                        "offset": 0,
                        "with": {
                            "analytics_data": False,
                            "barcodes": False,
                            "financial_data": False,
                            "translit": True
                        }
                    }

                    response = requests.post(url, headers=headers, json=payload)

                    # Проверяем успешность запроса
                    response.raise_for_status()

                    result = response.json()['result']
                    with open('ozon_shipments.json', 'w') as f:
                        json.dump(result, f, indent=2)
                    simplified_response = []
                    posting_numbers = []
                    for posting in result["postings"]:
                        simplified_response.append(
                            {
                                "marketplace_id": posting["posting_number"],
                                "status": posting["status"],
                                "shipment_date": posting["shipment_date"],
                                "products": posting["products"]
                            }
                        )
                        posting_numbers.append(posting['posting_number'])

                    for posting in simplified_response:
                        get_pdf(posting['marketplace_id'], user)
                        add_shipment_from_api(user, posting)

                except requests.exceptions.RequestException as e:
                    return None
    return render(request, 'sync_shipments.html')


def shipments(request):
    user = CustomUser.objects.filter(user=request.user).first()
    shipments = Shipment.objects.filter(seller=user, shipment_date__date=datetime.now().date()).order_by('shipment_date')
    return render(request, 'shipments.html', {'shipments': shipments})


def products(request):
    owners = CustomUser.objects.filter(user_type="seller")
    return render(request, 'products.html', {'owners': owners})


def change_status(request, posting_number):
    user = CustomUser.objects.filter(user=request.user)
    if user:
        user = user[0]
        if user.ozon_client_id and user.ozon_client_key:
            url = "https://api-seller.ozon.ru/v2/posting/fbs/awaiting-delivery"

            try:
                # Загрузка переменных из файла .env

                headers = {
                    "Client-Id": user.ozon_client_id,
                    "Api-Key": user.ozon_client_key
                }
                payload = {"posting_number": [posting_number]}

                response = requests.post(url, headers=headers, json=payload)

                # Проверяем успешность запроса
                response.raise_for_status()

                result = response.json()['result']
                if result:
                    shipment = Shipment.objects.get(marketplace_id=posting_number)
                    shipment.status = 'awaiting_deliver'
                    shipment.save()
                    get_pdf(shipment.posting_number, user)
            except requests.exceptions.RequestException as e:
                return None


def send_shipments(request):
    if request.method == "POST":

        user = CustomUser.objects.filter(user=request.user)
        if user:
            user = user[0]
            headers = {
                "Authorization": get_access_token()
            }
            # Данные о магазине, агенте и организации
            store_id = "a38602a8-df68-11ed-0a80-0c78000cbb45"
            organization_id = "a384b0a8-df68-11ed-0a80-0c78000cbb43"

            payload = {
                "store": {
                    "meta": {
                        "href": f"https://api.moysklad.ru/api/remap/1.2/entity/store/{store_id}",
                        "metadataHref": "https://api.moysklad.ru/api/remap/1.2/entity/store/metadata",
                        "type": "store",
                        "mediaType": "application/json",
                        "uuidHref": f"https://online.moysklad.ru/app/#warehouse/edit?id={store_id}"
                    }
                },
                "agent": {
                    "meta": {
                        "href": f"https://api.moysklad.ru/api/remap/1.2/entity/counterparty/{user.moysklad_id}",
                        "metadataHref": "https://api.moysklad.ru/api/remap/1.2/entity/counterparty/metadata",
                        "type": "counterparty",
                        "mediaType": "application/json",
                        "uuidHref": f"https://online.moysklad.ru/app/#company/edit?id={user.moysklad_id}"
                    }
                },
                "organization": {
                    "meta": {
                        "href": f"https://api.moysklad.ru/api/remap/1.2/entity/organization/{organization_id}",
                        "metadataHref": "https://api.moysklad.ru/api/remap/1.2/entity/organization/metadata",
                        "type": "organization",
                        "mediaType": "application/json",
                        "uuidHref": f"https://online.moysklad.ru/app/#mycompany/edit?id={organization_id}"
                    }
                },
                "positions": [],
                "files": []
            }

            today = datetime.now().date()
            tomorrow = today + timedelta(1)
            shipments = Shipment.objects.filter(seller=user, moysklad_id__isnull=True,
                                                shipment_date__lte=today + timedelta(1),
                                                shipment_date__gte=today).order_by('shipment_date')

            cur_date = shipments[0].shipment_date
            for shipment in shipments:
                if shipment.shipment_date == cur_date:
                    add_shipment_to_payload(payload, shipment)
                else:
                    try:
                        files = payload["files"]
                        payload["files"] = []
                        response = requests.post("https://api.moysklad.ru/api/remap/1.2/entity/demand", headers=headers,
                                                 json=payload)
                        with open(f'payload.json', 'w') as f:
                            json.dump(payload, f, indent=2)
                        response.raise_for_status()
                        shipment_id = response.json()["id"]
                        attach_pdfs_to_shipment(shipment_id, )
                        for date_shipment in shipments.filter(shipment_date=cur_date):
                            date_shipment.moysklad_id = shipment_id
                            date_shipment.save()
                        cur_date = shipment.shipment_date
                        payload["positions"] = []
                        payload["files"] = []
                        add_shipment_to_payload(payload, shipment)
                    except requests.exceptions.RequestException as e:
                        return None
            try:
                files = payload["files"]
                payload["files"] = []
                response = requests.post("https://api.moysklad.ru/api/remap/1.2/entity/demand", headers=headers,
                                         json=payload)
                with open(f'payload.json', 'w') as f:
                    json.dump(payload, f, indent=2)
                print(response.json())
                response.raise_for_status()
                shipment_id = response.json()["id"]
                attach_pdfs_to_shipment(shipment_id, files)
                for date_shipment in shipments.filter(shipment_date=cur_date):
                    date_shipment.moysklad_id = shipment_id
                    date_shipment.save()
            except requests.exceptions.RequestException as e:
                return None
    return render(request, 'send_shipments.html')
