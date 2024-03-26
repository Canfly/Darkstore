from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests
from .models import Shipment, Product
from .utils import update_product_from_api

import base64

from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, LoginForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            print(user)
            if user:
                login(request, user)
                redirect('sync_products')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


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

    return render(request, "sync.html")


def shipments(request):
    shipments = Shipment.objects.all()
    return render(request, 'shipments.html', {'shipments': shipments})
