from darkstore.celery import app
from celery.utils.log import get_task_logger
from celery import shared_task
from packaging.views import sync_products, sync_stocks
import requests

logger = get_task_logger(__name__)


@app.task
def call_sync_products():
    sync_products(None, True)


@app.task
def call_update_stocks():
    sync_stocks(None,True)
