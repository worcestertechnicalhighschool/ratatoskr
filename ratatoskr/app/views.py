import datetime
from functools import reduce
from io import UnsupportedOperation
from itertools import groupby
from django.http import HttpResponse
from django.core.mail import send_mail

import pandas as pd
from django.core.exceptions import PermissionDenied, BadRequest
from django.shortcuts import redirect, render
from django.utils import dateparse
from django.utils.timezone import make_aware
from app.calendarutil import build_calendar_client
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from googleapiclient.errors import HttpError

from ratatoskr.celery import debug_task, send_mail_task

from .forms import ReservationForm, ScheduleCreationForm, TimeslotGenerationForm
from .models import Schedule, TimeSlot, Reservation


@require_http_methods(["GET"])
def index(request):
    return render(request, 'app/pages/index.html', {
        "schedules": Schedule.objects.all()
    })


@require_http_methods(["GET", "POST"])
def create_schedule(request):
    if not request.user.is_authenticated:
        raise PermissionDenied()
    if request.method == "POST":
        form = ScheduleCreationForm(request.POST)
        if not form.is_valid():
            render(request, 'app/pages/create_schedule.html', {
                "errors": form.errors
            })  # TODO: Render form errors in template or something
        lock_date = datetime.datetime.now() + datetime.timedelta(days=99999)
        if form.cleaned_data.get("should_lock_automatically"):
            lock_date = form.cleaned_data.get("auto_lock_after")

        new_schedule = Schedule.objects.create(
            owner=request.user,
            name=form.cleaned_data["name"],
            auto_lock_after=make_aware(lock_date),
            is_locked=False,
        )
        return redirect("schedule", new_schedule.id)
    return render(request, 'app/pages/create_schedule.html', {})


@require_http_methods(["GET"])
def schedule(request, schedule):
    timeslots = schedule.timeslot_set.all()

    timeslots = dict(
        sorted(
            {k: list(v) for k, v in groupby(timeslots, lambda x: x.time_from.date())}.items()
            # Group the timeslots by their time_from date
        )
    )

    timeslot_meta = {
        k: {
            "from": v[0].time_from,
            "to": v[-1].time_to,
            "available": sum([i.reservation_limit for i in v]) - sum([i.reservation_set.count() for i in v]),
            "taken": sum([i.reservation_set.count() for i in v]),
            "all_locked": all([x.is_locked for x in v])
        } for k, v in timeslots.items()
    }

    return render(request, 'app/pages/schedule.html', {
        "schedule": schedule,
        "timeslots": timeslot_meta
    })


@require_http_methods(["GET"])
def user_schedules(request, user_id):
    if not request.user.is_authenticated:
        raise PermissionDenied()
    else:
        return render(request, "app/pages/schedules.html", {
            "schedules": Schedule.objects.filter(owner=user_id),
            "is_owner": request.user.id == user_id,
            "owner": User.objects.get(id=user_id)
        })


@require_http_methods(["GET"])
def schedule_day(request, schedule, date):
    timeslots = list(schedule.timeslot_set.all())

    return render(request, 'app/pages/schedule_day.html', {
        "schedule": schedule,
        "timeslots": filter(lambda x: x.time_from.date() == date.date(), timeslots),
        "date": date
    })


@require_http_methods(["POST"])
def schedule_edit(request, schedule):

    if schedule.owner != request.user:
        raise PermissionDenied()

    dates = [make_aware(datetime.datetime.strptime(i, '%Y-%m-%d')) for i in request.POST.getlist("timeslot_date")]
    ids = [int(i) for i in request.POST.getlist("timeslot_id")]

    # Query the timeslot table with all the data given
    # The "|"(union) operator effectively combines the two queries
    # I use a reduce to merge a list of queries into one singular query, using said union opeartor
    timeslot_date_query = [
        TimeSlot.objects.filter(schedule=schedule, time_from__range=(date, date + datetime.timedelta(hours=24)))
        for date in dates
    ]
    timeslot_date_query = reduce(lambda a, x: a | x, timeslot_date_query, TimeSlot.objects.none())
    timeslot_id_query = [TimeSlot.objects.filter(schedule=schedule, pk=id) for id in ids]
    timeslot_id_query = reduce(lambda a, x: a | x, timeslot_id_query, TimeSlot.objects.none())
    timeslots = (timeslot_date_query | timeslot_id_query)
    all_timeslots = timeslots.all()

    match request.POST["action"]:
        case "lock":
            for timeslot in all_timeslots:
                timeslot.is_locked = True
            TimeSlot.objects.bulk_update(all_timeslots, ["is_locked"])
        case "unlock":
            for timeslot in all_timeslots:
                timeslot.is_locked = False
            TimeSlot.objects.bulk_update(all_timeslots, ["is_locked"])
        case "delete":
            timeslots.delete()

    return redirect(request.GET.get("next") or "/")


@require_http_methods(["GET", "POST"])
def create_timeslots(request, schedule):

    if schedule.owner != request.user:
        raise PermissionDenied()

    if request.POST:
        form = TimeslotGenerationForm(request.POST)
        if not form.is_valid():
            return render(request, "app/pages/create_timeslots.html", {"errors": form.errors})

        # The "-" operator only works on datetime objects and not time. Just use datetime.combine to get a datetime with the needed times to get the delta of
        from_time = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["from_time"])
        to_time = datetime.datetime.combine(form.cleaned_data["to_date"], form.cleaned_data["to_time"])

        if not form.cleaned_data["multiple_timeslots"]:
            TimeSlot(
                schedule=schedule,
                time_from=make_aware(from_time),
                time_to=make_aware(to_time),
                reservation_limit=form.cleaned_data["openings"],
                is_locked=False,
                auto_lock_after=make_aware(datetime.datetime.now() + datetime.timedelta(days=500000))
            ).save()
        else:
            # We need to create a dict with keys from DateA to DateB where
            # each date has an array of times that go from TimeA to TimeB.

            # So if we need to create timeslots:
            # from 3/10 to 3/12
            # from 1:00 to 2:00
            # with 20 minutes for each timeslot
            # with a 10 minutes buffer in between each timeslot
            # we would get the following result:
            # (mind the pseudo-code)
            #   3/10: Timeslot(1:00-1:20), Timeslot(1:30-1:50)
            #   3/11: Timeslot(1:00-1:20), Timeslot(1:30-1:50)
            #   3/12: Timeslot(1:00-1:20), Timeslot(1:30-1:50)
            # Note how there are 10 minutes in between the timeslot for (1:00, 1:20) and (1:30, 1:50).
            # Thats the 10 minute buffer.

            # To create this data, we need to do some timedelta operations starting from a base time.
            # Let 1:00 be our base time.
            # Let 20 minutes be our length
            # Let 30 minutes be the total_buffer (length + buffer)

            # Now, Lets step through that big scary list comprehension below.
            # Starting off, we have a 0 minutes offset
            # Time from will be: 1:00 + 0 minutes = 1:00 
            # Time to will be: 1:00 + 0 minutes + 20 minutes = 1:20

            # On the next iteration, we will increase our offset by the total_buffer, 30 minutes
            # Time from will be: 1:00 + 30 minutes = 1:30
            # Time to will be: 1:00 + 30 minutes + 20 minutes = 1:50

            # This will result in the following timeslots:
            # Timeslot(1:00-1:20), Timeslot(1:30-1:50)

            # Do this for every date and now we have all the timeslots from 3/10 to 3/12
            
            # Our date range
            dates = pd.date_range(form.cleaned_data["from_date"], form.cleaned_data["to_date"])
            # The total amount of time from the first timeslot's start to the last timeslot's end
            time_delta = to_time - from_time
            time_delta_mins = int(time_delta.seconds / 60)
            # Total amount of time the timeslot will take up
            length = form.cleaned_data["timeslot_length"]
            break_length = form.cleaned_data["timeslot_break"]
            # ...now including the break inbetween
            total_buffer = length + break_length

            # This is the data we need as described above
            timeslot_times = [
                [
                    TimeSlot(
                        schedule=schedule,
                        time_from=make_aware(
                            datetime.datetime.combine(
                                date, (from_time + datetime.timedelta(minutes=minute_offset)).time()
                            )
                        ),
                        time_to=make_aware(
                            datetime.datetime.combine(
                                date, (from_time + datetime.timedelta(minutes=minute_offset + length)).time()
                            )
                        ),
                        reservation_limit=form.cleaned_data["openings"],
                        is_locked=False,
                        auto_lock_after=make_aware(datetime.datetime.now() + datetime.timedelta(days=500000))
                    ) for minute_offset in range(0, time_delta_mins, total_buffer)
                ] for date in dates
            ]

            # Since we get a 2d array from this, we need to flatten it
            objects = sum(timeslot_times.values(), [])

            TimeSlot.objects.bulk_create(objects)

        return redirect("schedule", schedule.id)

    return render(request, "app/pages/create_timeslots.html", {})


@require_http_methods(["GET", "POST"])
def reserve_timeslot(request, schedule, date, timeslot):
    reservations = Reservation.objects.filter(timeslot=timeslot).count()
    if timeslot.is_locked or reservations >= timeslot.reservation_limit:
        raise PermissionDenied()
    if request.POST:
        reservation_form = ReservationForm(request.POST)
        if not reservation_form.is_valid():
            return render(request, "app/pages/reserve_timeslot.html", {
                "schedule": schedule,
                "timeslot": timeslot,
                "form": reservation_form
            })
        Reservation.objects.create(
            timeslot=timeslot,
            comment=reservation_form.cleaned_data["comment"],
            email=reservation_form.cleaned_data["email"],
            name=reservation_form.cleaned_data["name"],
        )
        return redirect("reserve-confirmed")
    return render(request, "app/pages/reserve_timeslot.html", {
        "schedule": schedule,
        "timeslot": timeslot,
        "form": ReservationForm()
    })


@require_http_methods(["GET", "POST"])
def view_reservations(request, schedule, date, timeslot):
    if schedule.owner.id != request.user.id:
        raise PermissionDenied()

    reservations = timeslot.reservation_set.all()

    if request.POST:
        # Just in case there will be more actions in the future.
        match request.POST["action"]:
            case "cancel":
                Reservation.objects.filter(pk=request.POST["id"]).delete()

    return render(request, "app/pages/reservations_view.html", {
        "timeslot": timeslot,
        "schedule": schedule,
        "reservations": reservations
    })


@require_http_methods(["GET", "POST"])
def view_schedule_reservations(request, schedule):
    if schedule.owner.id != request.user.id:
        raise PermissionDenied()

    if request.POST:
        # Just in case there will be more actions in the future.
        match request.POST["action"]:
            case "cancel":
                Reservation.objects.filter(pk=request.POST["id"]).delete()

    timeslots = schedule.timeslot_set.all()

    # This groups up all reservations into 
    # Key: Date
    # Value: Timeslots that land on date
    reservations = {
        date["timeslot__time_from__date"]: Reservation.objects.filter(
            timeslot__time_from__date=date["timeslot__time_from__date"]
        )
        # Get all dates
        for date in (
            Reservation.objects.filter(timeslot__schedule=schedule)
                .all()
                .values("timeslot__time_from__date")
                .distinct()
        )
    }.items()

    return render(request, "app/pages/reservations_view_schedule.html",
                  {"schedule": schedule, "timeslots": reservations})


@require_http_methods(["GET"])
def reserve_confirmed(request):
    return render(request, "app/pages/reserve_confirmed.html", {

    })


def test(request, schedule):
    return HttpResponse(schedule.id)
