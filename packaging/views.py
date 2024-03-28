from datetime import datetime, timedelta

from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests
from .models import Shipment, Product, CustomUser
from .utils import update_product_from_api, update_stocks_from_api, add_shipment_from_api
import json

import base64

from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, RegisterForm


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


def sync_products(request=None, celery=False):
    """Syncs products from MoySklad."""
    LOGIN = "sklad@fillrufill"
    PASSWORD = "FillRu2024Password"
    URL_API = "https://api.moysklad.ru/api/remap/1.2/entity/product"
    headers = {"Authorization": get_access_token()}

    if request.method == "POST" or celery == True:
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

    if request.method == "POST" or celery == True:
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
    def get_pdf(posting_number):
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

            with open(f"package-labels/output_{posting_number}.pdf", "wb") as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            return None

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

                    date_from = datetime.utcnow()
                    date_to = datetime.utcnow() + timedelta(hours=48)

                    payload = {
                        "dir": "ASC",
                        "filter": {
                            "cutoff_from": date_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "cutoff_to": date_to.strftime("%Y-%m-%dT%H:%M:%SZ")
                        },
                        "limit": 15,
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
                        if posting['status'] == 'awaiting_deliver':
                            get_pdf(posting['marketplace_id'])
                        add_shipment_from_api(user, posting)

                except requests.exceptions.RequestException as e:
                    return None
    return render(request, 'sync_shipments.html')


def shipments(request):
    shipments = Shipment.objects.all()
    return render(request, 'shipments.html', {'shipments': shipments})


def products(request):
    owners = CustomUser.objects.all()
    for owner in owners:
        print(owner.product_set.all())
    return render(request, 'products.html', {'owners': owners})
