from base64 import b64encode
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from googleapiclient.errors import HttpError
from threading import Thread
from simple_history.models import HistoricalRecords

from .calendarutil import create_calendar_for_schedule, delete_calendar_for_schedule, delete_timeslot_event, \
    update_timeslot_event, add_subscriber, remove_subscriber, change_visibility

# Create your models here.
from .emailutil import send_change_email, send_cancelled_email


class Schedule(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = 'A'
        UNLISTED = 'U'
        PRIVATE = 'P'

    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=1, choices=Visibility.choices, default=Visibility.PUBLIC)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=1000, default="")
    is_locked = models.BooleanField()
    auto_lock_after = models.DateTimeField()
    # These fields are filled automatically
    calendar_id = models.CharField(max_length=1024)
    calendar_meet_data = models.JSONField()

    def get_calendar_url(self):
        # Direct link to calendar. cid is base 64 encoded
        # For some reason, b64encode has these two "==" at the end of the decoded string, so I just striped them out.
        return f"https://calendar.google.com/calendar/u/0?cid={b64encode(self.calendar_id.encode('ascii')).decode('ascii')[:-2]}"


class TimeSlot(models.Model):
    id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(to=Schedule, on_delete=models.CASCADE)
    time_from = models.DateTimeField()
    time_to = models.DateTimeField()
    auto_lock_after = models.DateTimeField()
    is_locked = models.BooleanField()
    reservation_limit = models.IntegerField()


class Reservation(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True)
    name = models.CharField(max_length=747)
    timeslot = models.ForeignKey(to=TimeSlot, on_delete=models.CASCADE)
    email = models.EmailField()
    comment = models.CharField(max_length=256)
    confirmed = models.BooleanField(default=False)
    history = HistoricalRecords()


class ScheduleSubscription(models.Model):
    id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(to=Schedule, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    add_as_guest = models.BooleanField(default=False)
    history = HistoricalRecords()


# Signals for hooking into Google Calendar API


@receiver(models.signals.pre_save, sender=Schedule)
def on_schedule_create(sender, instance, **kwargs):
    if instance.pk is not None:
        old = Schedule.objects.filter(pk=instance.pk).get()
        if old.visibility != instance.visibility: change_visibility(instance)
        return
    (instance.calendar_meet_data, instance.calendar_id) = create_calendar_for_schedule(instance)


@receiver(models.signals.post_delete, sender=Schedule)
def on_schedule_delete(sender, instance, **kwargs):
    delete_calendar_for_schedule(instance)


@receiver(models.signals.post_save, sender=Reservation)
def on_reservation_create(sender, instance, **kwargs):
    try:
        update_timeslot_event(instance.timeslot)
    except HttpError as e:
        instance.delete()
        raise e


@receiver(models.signals.post_save, sender=Reservation)
def on_reservation_changed(sender, instance, **kwargs):
    if instance.confirmed:
        send_change_email(instance, "confirmed")


@receiver(models.signals.post_delete, sender=Reservation)
def on_reservation_delete(sender, instance, **kwargs):
    send_change_email(instance, "cancelled")
    send_cancelled_email(instance)
    update_timeslot_event(instance.timeslot)


@receiver(models.signals.post_delete, sender=TimeSlot)
def on_timeslot_delete(sender, instance, **kwargs):
    delete_timeslot_event(instance)


@receiver(models.signals.post_save, sender=ScheduleSubscription)
def on_subscription_created(sender, instance, created, **kwargs):
    if instance.add_as_guest: add_subscriber(instance.schedule, instance.user)
    elif not instance.add_as_guest and not created: remove_subscriber(instance.schedule, instance.user)


@receiver(models.signals.post_delete, sender=ScheduleSubscription)
def on_subscription_delete(sender, instance, **kwargs):
    if instance.add_as_guest: remove_subscriber(instance.schedule, instance.user)