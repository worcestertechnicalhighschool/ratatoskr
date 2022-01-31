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

    return render(request, 'app/pages/schedule.html', {
        "schedule": schedule,
        "timeslots": dict(
            sorted(
                { k: list(v) for k, v in groupby(timeslots, lambda x: x.time_from.date()) }.items() # Group the timeslots by their time_from date
            )
        )
    })

def schedule_day(request, schedule_id, date):
    schedule = Schedule.objects.get(pk=schedule_id)
    timeslots = TimeSlot.objects.filter(schedule=schedule)

    return render(request, 'app/pages/schedule_day.html', {
        "schedule": schedule,
        "timeslots": filter(lambda x: x.time_from.date() == date.date(), timeslots),
        "date": date
    })

def create_timeslots(request, schedule_id):
    if request.POST:
        schedule = Schedule.objects.get(pk=schedule_id)
        form = TimeslotGenerationForm(request.POST)
        if not form.is_valid():
            return render(request, "app/pages/create_timeslots.html", {
                "form": form
            })
        
        dates = pd.date_range(form.cleaned_data["from_date"], form.cleaned_data["to_date"])
        from_time = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["from_time"])
        to_time = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["to_time"])
        time_delta = to_time - from_time
        time_delta_mins = int(time_delta.seconds / 60)

        base = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["from_time"])
        length = form.cleaned_data["timeslot_length"]
        break_length = form.cleaned_data["timeslot_break"]
        total_buffer = length + break_length

        # To the poor student who has to maintain this code in 3 years time: Good luck lmao
        timeslot_times = [[(i, (base + datetime.timedelta(minutes=j)).time(), (base + datetime.timedelta(minutes=j + length)).time()) for j in range(0, time_delta_mins+1, total_buffer)] for i in dates]

        flattened = sum(timeslot_times, [])

        for date, time_from, time_to in flattened:
            TimeSlot.objects.create(
                schedule = schedule,
                time_from = make_aware(datetime.datetime.combine(date, time_from)),
                time_to = make_aware(datetime.datetime.combine(date, time_to)),
                reservation_limit = form.cleaned_data["openings"],
                is_locked = False,
                auto_lock_after = make_aware(datetime.datetime.now() + datetime.timedelta(days=500000))
            )

        return redirect("schedule", schedule_id)
        
    return render(request, "app/pages/create_timeslots.html", {
        "form": TimeslotGenerationForm()
    })