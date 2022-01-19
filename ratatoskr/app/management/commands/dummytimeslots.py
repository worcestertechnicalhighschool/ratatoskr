from datetime import datetime, timedelta
from time import time
from allauth.socialaccount import providers
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from allauth.socialaccount.models import SocialApp
from app.models import TimeSlot, Schedule

class Command(BaseCommand):
    help = 'Delete this as soon as we have schedule submition functionality'

    def handle(self, *args, **options):
        schedule_id = int(input("Schedule Id?: "))
        day_delta = int(input("Day Delta?: "))
        schedule = Schedule.objects.get(pk=schedule_id)
        for i in range(1, 10):
            TimeSlot.objects.create(
                schedule=schedule,
                time_from = datetime.now() + timedelta(days=day_delta),
                time_to = datetime.now() + timedelta(minutes=120 + (i * 5)),
                auto_lock_after = datetime.now() + timedelta(hours=9999999),
                is_locked = False,
                reservation_limit = 99999
            )

