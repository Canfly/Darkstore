from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
from .models import Shipment, Product
from .utils import update_product_from_api

import base64

from django.contrib.auth.forms import UserCreationForm


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
        #print(response.json())
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
