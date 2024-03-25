from __future__ import absolute_import
import os
from celery import Celery

# Настройка брокера сообщений
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')

# Настройка очереди задач
CELERY_QUEUES = {
    'default': {
        'exchange': 'default',
        'binding_key': 'default',
    },
}

# Настройка задач
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'

app = Celery('darkstore', broker='redis://localhost:6379')

# Optional: Автоматическое обнаружение задач
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    'update_product_quantity_in_stock': {
        'task': 'tasks.update_product_quantity_in_stock',
        'schedule': crontab(minute='*/10'),  # Каждые 10 минут
        'args': (),
    }}
