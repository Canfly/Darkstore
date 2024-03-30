"""
Этот код предназначен для получения информации о возвратах товаров
из Ozon API и сохранения ее в JSON-файл.

* Получение данных о возвратах товаров со статусом "waiting_for_seller".
* Сохранение данных в JSON-файл с уникальным именем.

**Требования:**

* Библиотеки requests, json и logging.
* Файл .env с переменными OZON_CLIENT_ID и OZON_API_KEY.
"""

import os
import requests
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Настройка логгера

log_file = 'script_log.txt'
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройка

default_payload = {
    "filter": {
        "status": "waiting_for_seller"
    },
    "limit": 100
}

def_id = '74350'
def_token = '918127b6-1c98-448a-a374-7430ec769a74'


def get_ozon_returns(ozon_id=def_id, ozon_token=def_token, filter=default_payload):
    """
    Функция для получения информации о возвратах товаров из Ozon API.

    Args:
        filter (dict): Параметры фильтрации.

    Returns:
        dict: Ответ от Ozon API.
    """

    url = "https://api-seller.ozon.ru/v3/returns/company/fbs"

    try:

        headers = {
            "Client-Id": ozon_id,
            "Api-Key": ozon_token
        }

        response = requests.post(url, headers=headers, json=filter)

        # Проверяем успешность запроса
        response.raise_for_status()

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


def main():
    """
    Главная функция.
    """

    # Получаем данные от Ozon API
    response = get_ozon_returns()

    # Сохраняем данные в JSON-файл
    current_time = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    json_file_name = f"data_{current_time}.json"
    save_json(response, json_file_name)


if __name__ == "__main__":
    main()
