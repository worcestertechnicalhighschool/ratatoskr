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
            render(request, "app/pages/create_timeslots.html", {
                "form": form
            })
        redirect("schedule", schedule_id)
        
    return render(request, "app/pages/create_timeslots.html", {
        "form": TimeslotGenerationForm()
    })