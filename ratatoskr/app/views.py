from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.utils import dateparse, timezone
from .models import Schedule, TimeSlot, Reservation
import datetime

# Create your views here.
def index(request):
    return render(request, 'app/pages/index.html', {})

def create_schedule(request):
    if not request.user.is_authenticated:
        raise PermissionDenied()
    if request.method == "POST":
        lock_date = datetime.datetime.now() + datetime.timedelta(days=99999)
        if request.POST.get("should_lock_automatically") == "on":
            lock_date = dateparse.parse_datetime(request.POST.get("auto_lock_after"))
        Schedule.objects.create(
            owner = request.user,
            name = request.POST.get("name"),
            auto_lock_after = lock_date,
            is_locked = False
        )

    return render(request, 'app/pages/create_schedule.html', {})
