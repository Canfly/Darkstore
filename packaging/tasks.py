from celery import shared_task
from .models import User
from django_celery_beat.models import PeriodicTask


@shared_task(name='update_shipments')
def update_shipments():
    print('ГОВНОГОВНОГОВНОГОВНОГОВНО')
    task = PeriodicTask.objects.get()
    task.enabled = False
    task.save()
    User.objects.create(name='TEST')
