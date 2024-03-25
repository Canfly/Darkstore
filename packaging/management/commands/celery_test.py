import json

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    def handle(self, *args, **options):
        shedule = IntervalSchedule.objects.get_or_create(every=10, period='seconds')
        print(shedule[0])
        task = PeriodicTask.objects.create(
            name='celery_test',
            task='update_shipments',
            interval=shedule[0],
            start_time=timezone.now(),
        )

