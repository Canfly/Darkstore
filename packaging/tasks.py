from darkstore.celery import app
from celery.utils.log import get_task_logger
from views import sync_products, sync_stocks
import requests

logger = get_task_logger(__name__)


@app.task
def sync_products():
    sync_products(celery=True)


@app.task
def update_stocks():
    sync_stocks(celery=True)
