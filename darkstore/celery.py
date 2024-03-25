from __future__ import absolute_import
import os
from celery import Celery
from tasks import taskone

# Настройка брокера сообщений
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379')

# Настройка задач
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'

app = Celery('darkstore', broker='redis://localhost:6379')

# Optional: Автоматическое обнаружение задач
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
       'taskone': {
          'task': 'tasks.taskone',
          'schedule': crontab(minute='*/10'), # Каждые 10 секунд
          'args': (),
       }}
