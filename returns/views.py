from django.shortcuts import render
import os
import requests
import json
import logging
from datetime import datetime, timedelta
from barcode import generate
from packaging.models import CustomUser
import cairosvg

# from funcs import get_ozon_returns
# from .models import Product


default_payload = {
    "filter": {
        "status": "waiting_for_seller"
    },
    "limit": 100
}


def get_ozon_returns(request, filter=default_payload):
    """
    Функция для получения информации о возвратах товаров из Ozon API.

    Args:
        filter (dict): Параметры фильтрации.

    Returns:
        dict: Ответ от Ozon API.
    """

    url = "https://api-seller.ozon.ru/v3/returns/company/fbs"

    user = CustomUser.objects.filter(user=request.user).first()

    try:

        headers = {
            "Client-Id": user.ozon_client_id,
            "Api-Key": user.ozon_client_key,
        }

        response = requests.post(url, headers=headers, json=filter)

        # Проверяем успешность запроса
        response.raise_for_status()
        print(response.json())

        logging.info("+ Request to Ozon API successful")
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Error during request: {str(e)}")
        return None


def save_json(data, filename):
    """
    Функция для сохранения данных в JSON-файл.

    Args:
        data (dict): Данные для сохранения.
        filename (str): Имя файла.
    """

    try:
        with open(filename, "w") as fp:
            json.dump(data, fp, indent=4)
        logging.info(f"Data saved to file {filename}")
    except Exception as e:
        logging.error(f"Error saving data: {str(e)}")


def get_barcode(request):
    user = CustomUser.objects.filter(user=request.user).first()

    headers = {
        "Client-Id": user.ozon_client_id,
        "Api-Key": user.ozon_client_key,
    }

    def get_ozon_available_returns():
        url = "https://api-seller.ozon.ru/v1/return/giveout/is-enabled"

        try:
            # Загрузка значений из переменных окружения

            response = requests.post(url, headers=headers)

            # Проверяем успешность запроса
            response.raise_for_status()

            logging.info("+ Request to Ozon API successful")
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Error during request: {str(e)}")
            return None

    def get_ozon_returns_barcode():
        url = "https://api-seller.ozon.ru/v1/return/giveout/barcode"

        try:
            # Загрузка переменных из файла .env

            # Загрузка значений из переменных окружения

            response = requests.post(url, headers=headers)

            # Проверяем успешность запроса
            response.raise_for_status()

            logging.info("+ Request to Ozon API successful")
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"Error during request: {str(e)}")
            return None

    def createBarCodes(s):
        generate('code128', s, output='static/returns/images/barcode')

    return_status = get_ozon_available_returns()['enabled']
    if return_status:
        return_barcode = get_ozon_returns_barcode()
        print(return_barcode['barcode'])
        createBarCodes(return_barcode['barcode'])
        # Генерируем уникальные имена файлов на основе текущего времени
        current_time = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        json_file_name = f"data.json"

        with open(json_file_name, 'w') as fp:
            json.dump(return_barcode, fp, indent=4)


def return_list(request):
    products = get_ozon_returns(request)  # Замените на вашу модель продукта

    return render(request, 'return_list.html', {'products': products})


def generate_barcode(request):
    get_barcode(request)
    return render(request, 'barcode.html')
