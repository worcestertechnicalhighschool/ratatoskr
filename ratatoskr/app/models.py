from django.db import models
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from googleapiclient.errors import HttpError

from .calendarutil import create_calendar_for_schedule, delete_timeslot_event, update_timeslot_event

# Create your models here.

class Schedule(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    is_locked = models.BooleanField()
    auto_lock_after = models.DateTimeField()
    # These fields are filled automatically
    calendar_id = models.CharField(max_length=1024)
    calendar_meet_data = models.JSONField()

class TimeSlot(models.Model):
    id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(to=Schedule, on_delete=models.CASCADE)
    time_from = models.DateTimeField()
    time_to = models.DateTimeField()
    auto_lock_after = models.DateTimeField()
    is_locked = models.BooleanField()
    reservation_limit = models.IntegerField()

class Reservation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=747)
    timeslot = models.ForeignKey(to=TimeSlot, on_delete=models.CASCADE)
    email = models.EmailField()
    comment = models.CharField(max_length=256)

@receiver(models.signals.pre_save, sender=Schedule)
def on_schedule_create(sender, instance, **kwargs):
    if instance.pk is not None:
        return
    (instance.calendar_meet_data, instance.calendar_id) = create_calendar_for_schedule(instance)

@receiver(models.signals.post_save, sender=Reservation)
def on_reservation_create(sender, instance, **kwargs):
    try:
        update_timeslot_event(instance.timeslot)
    except HttpError as e:
        instance.delete()
        raise e

@receiver(models.signals.post_delete, sender=Reservation)
def on_reservation_create(sender, instance, **kwargs):
    update_timeslot_event(instance.timeslot)

@receiver(models.signals.post_delete, sender=TimeSlot)
def on_timeslot_delete(sender, instance, **kwargs):
    delete_timeslot_event(instance)