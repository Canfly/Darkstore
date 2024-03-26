from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests
from .models import Shipment, Product,CustomUser
from .utils import update_product_from_api, update_stocks_from_api
import json

import base64

from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, RegisterForm

def home(request):
    pass

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


def sync_products(request):
    """Syncs products from MoySklad."""
    LOGIN = "sklad@fillrufill"
    PASSWORD = "FillRu2024Password"
    URL_API = "https://api.moysklad.ru/api/remap/1.2/entity/product"
    headers = {"Authorization": get_access_token()}

    if request.method == "POST":
        response = requests.get(URL_API, headers=headers)
        # print(response.json())
        if response.status_code == 200:
            products = []
            for product in response.json()["rows"]:
                product_id = update_product_from_api(product["code"], product)
                products.append({"sku": product_id, "name": product["name"]})
            return JsonResponse(products, safe=False)
        else:
            return HttpResponse(status=500)

    return render(request, "sync_products.html")


def sync_stocks(request):
    """Syncs products from MoySklad."""
    LOGIN = "sklad@fillrufill"
    PASSWORD = "FillRu2024Password"
    URL_API = "https://api.moysklad.ru/api/remap/1.2/report/stock/all"
    headers = {"Authorization": get_access_token()}
    response = requests.get(URL_API, headers=headers)

    if request.method == "POST":
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


def shipments(request):
    shipments = Shipment.objects.all()
    return render(request, 'shipments.html', {'shipments': shipments})


def products(request):
    owners = CustomUser.objects.all()
    for owner in owners:
        print(owner.product_set.all())
    return render(request, 'products.html', {'owners': owners})
