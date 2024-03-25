from __future__ import absolute_import,unicode_literals
import os
from celery import Celery

# Настройка брокера сообщений

# Настройка очереди задач
"""
All info about setting up is here 
https://episyche.com/blog/how-to-run-periodic-tasks-in-django-using-celery
"""


os.environ.setdefault("DJANGO_SETTINGS_MODULE","darkstore.settings")


app = Celery('celery_app', broker = 'redis://localhost:6379/0',
    backend = 'redis://localhost:6379/0')


app.config_from_object('django.conf:settings', namespace='CELERY')

# Optional: Автоматическое обнаружение задач
app.autodiscover_tasks()

