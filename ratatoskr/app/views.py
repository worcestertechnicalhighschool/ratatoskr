from io import UnsupportedOperation
import re
from sqlite3 import Time
from tokenize import group
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.utils import dateparse, timezone
from django.utils.timezone import make_aware

from .forms import TimeslotGenerationForm
from .models import Schedule, TimeSlot, Reservation
import datetime
from itertools import groupby
import pandas as pd

# Create your views here.
def index(request):
    return render(request, 'app/pages/index.html', {
        "schedules": Schedule.objects.all()
    })

def create_schedule(request):
    if not request.user.is_authenticated:
        raise PermissionDenied()
    if request.method == "POST":
        lock_date = datetime.datetime.now() + datetime.timedelta(days=99999)
        if request.POST.get("should_lock_automatically") == "on":
            lock_date = dateparse.parse_datetime(request.POST.get("auto_lock_after"))
        new_schedule = Schedule.objects.create(
            owner = request.user,
            name = request.POST.get("name"),
            auto_lock_after = make_aware(lock_date),
            is_locked = False
        )
        return redirect("schedule", new_schedule.id)

    return render(request, 'app/pages/create_schedule.html', {})

def schedule(request, schedule_id):
    schedule = Schedule.objects.get(pk=schedule_id)
    timeslots = TimeSlot.objects.filter(schedule=schedule)

    timeslots = dict(
            sorted(
                { k: list(v) for k, v in groupby(timeslots, lambda x: x.time_from.date()) }.items() # Group the timeslots by their time_from date
            )
        )
    
    timeslot_meta = {
        k: {
            "from": v[0].time_from,
            "to": v[-1].time_to,
            "available": 999, # TODO: Implement a way to find these stats
            "taken": 999
        } for k, v in timeslots.items()
    }

    return render(request, 'app/pages/schedule.html', {
        "schedule": schedule,
        "timeslots": timeslot_meta
    })

def schedule_day(request, schedule_id, date):
    schedule = Schedule.objects.get(pk=schedule_id)
    timeslots = TimeSlot.objects.filter(schedule=schedule)

    return render(request, 'app/pages/schedule_day.html', {
        "schedule": schedule,
        "timeslots": filter(lambda x: x.time_from.date() == date.date(), timeslots),
        "date": date
    })

# Deletes timeslots
def schedule_delete(request, schedule_id):
    if not request.POST:
        raise UnsupportedOperation()

    schedule = Schedule.objects.filter(pk=schedule_id).get()

    if schedule.owner != request.user:
        pass

    dates = [datetime.datetime.strptime(i, '%Y-%m-%d') for i in request.POST.getlist("timeslot_date")]
    timeslot_ids = [int(i) for i in request.POST.getlist("timeslot_id")]

    # Query with schedule to prevent someone deleting timeslots using another schedule's id
    for date in dates:
        TimeSlot.objects.filter(schedule=schedule, time_from__range=(date, date + datetime.timedelta(hours=24))).delete()
    for id in timeslot_ids:
        TimeSlot.objects.filter(schedule=schedule, pk=id).delete()

    return redirect("schedule", schedule_id)

# Toggles locking of timeslots
def schedule_lock(request, schedule_id):
    if not request.POST:
        raise UnsupportedOperation()

    schedule = Schedule.objects.filter(pk=schedule_id).get()

    if schedule.owner != request.user:
        pass

    dates = [datetime.datetime.strptime(i, '%Y-%m-%d') for i in request.POST.getlist("timeslot_date")]
    timeslot_ids = [int(i) for i in request.POST.getlist("timeslot_id")]

    # Query with schedule to prevent someone deleting timeslots using another schedule's id
    for date in dates:
        for timeslot in TimeSlot.objects.filter(schedule=schedule, time_from__range=(date, date + datetime.timedelta(hours=24))).all():
            timeslot.is_locked = not timeslot.is_locked
            timeslot.save()
    for id in timeslot_ids:
        for timeslot in TimeSlot.objects.filter(schedule=schedule, pk=id).all():
            timeslot.is_locked = not timeslot.is_locked
            timeslot.save()

    return redirect("schedule", schedule_id)


def create_timeslots(request, schedule_id):
    if request.POST:
        schedule = Schedule.objects.get(pk=schedule_id)
        form = TimeslotGenerationForm(request.POST)
        if not form.is_valid():
            return render(request, "app/pages/create_timeslots.html", {
                "form": form
            })
        
        dates = pd.date_range(form.cleaned_data["from_date"], form.cleaned_data["to_date"])
        # The "-" operator only works on datetime objects and not time. Just use datetime.combine to get a datetime with the needed times to get the delta of
        from_time = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["from_time"])
        to_time = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["to_time"])
        time_delta = to_time - from_time
        time_delta_mins = int(time_delta.seconds / 60)

        
        base = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["from_time"])
        length = form.cleaned_data["timeslot_length"]
        break_length = form.cleaned_data["timeslot_break"]
        total_buffer = length + break_length

        # To the poor student who has to maintain this code in 2 years time: Good luck lmao
        # Listen closely, as I will attempt to explain what the heck is going on in this hellspawn of a list comprehension
        # base, as defined earlier, will represent the start of the list of timeslots. Ignore the date component, I just made it a datetime so I can do timedelta operations on it.
        # I iterate over every date in the date range created earlier (dates)
        # For each of these, I use range to get every offset available for each timeslot, from 0 (no offset) to time_delta_mins (max offset)
        # total_buffer is the combined time of the length of each timeslot and the length of the breaks between the timeslots. I use this as the skip parameter for range. This should create the timeslots with the appropriate time for the meeting and the break time in between
        # For every available offset, I make a tuple containing:
        # The date
        # The base plus the offset
        # The base plus the offset and the length of the meeting
        # Thats all I can say about this horrible thing
        # Good luck
        timeslot_times = [[(date, (base + datetime.timedelta(minutes=minute_offset)).time(), (base + datetime.timedelta(minutes=minute_offset + length)).time()) for minute_offset in range(0, time_delta_mins, total_buffer)] for date in dates]

        # The resulting list will be a 2d list, with each list being the timeslots for one day.
        # Each list is a list of tuples with the following data:
        # Date, time_from, time_to
        flattened = sum(timeslot_times, [])

        objects = [
            TimeSlot(
                schedule = schedule,
                time_from = make_aware(datetime.datetime.combine(date, time_from)),
                time_to = make_aware(datetime.datetime.combine(date, time_to)),
                reservation_limit = form.cleaned_data["openings"],
                is_locked = False,
                auto_lock_after = make_aware(datetime.datetime.now() + datetime.timedelta(days=500000))
            ) for date, time_from, time_to in flattened
        ]

        TimeSlot.objects.bulk_create(objects)

        return redirect("schedule", schedule_id)
        
    return render(request, "app/pages/create_timeslots.html", {
        "form": TimeslotGenerationForm()
    })
