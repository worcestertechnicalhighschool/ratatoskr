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
        valid = form.is_valid()
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
def schedule(request, schedule_id):
    schedule = Schedule.objects.get(pk=schedule_id)
    timeslots = TimeSlot.objects.filter(schedule=schedule)

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
def schedule_day(request, schedule_id, date):
    schedule = Schedule.objects.get(pk=schedule_id)
    timeslots = TimeSlot.objects.filter(schedule=schedule)

    return render(request, 'app/pages/schedule_day.html', {
        "schedule": schedule,
        "timeslots": filter(lambda x: x.time_from.date() == date.date(), timeslots),
        "date": date
    })


@require_http_methods(["POST"])
def schedule_edit(request, schedule_id):
    schedule = Schedule.objects.filter(pk=schedule_id).get()

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
def create_timeslots(request, schedule_id):
    schedule = Schedule.objects.get(pk=schedule_id)

    if schedule.owner != request.user:
        raise PermissionDenied()

    if request.POST:
        form = TimeslotGenerationForm(request.POST)
        if not form.is_valid():
            return render(request, "app/pages/create_timeslots.html", {"errors": form.errors})

        dates = pd.date_range(form.cleaned_data["from_date"], form.cleaned_data["to_date"])
        # The "-" operator only works on datetime objects and not time. Just use datetime.combine to get a datetime with the needed times to get the delta of
        from_time = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["from_time"])
        to_time = datetime.datetime.combine(form.cleaned_data["to_date"], form.cleaned_data["to_time"])
        time_delta = to_time - from_time
        time_delta_mins = int(time_delta.seconds / 60)

        base = datetime.datetime.combine(form.cleaned_data["from_date"], form.cleaned_data["from_time"])

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
            length = form.cleaned_data["timeslot_length"]
            break_length = form.cleaned_data["timeslot_break"]
            total_buffer = length + break_length

            # To the poor student who has to maintain this code in 2 years time: Good luck lmao Listen closely,
            # as I will attempt to explain what the heck is going on in this hellspawn of a list comprehension base,
            # as defined earlier, will represent the start of the list of timeslots. Ignore the date component,
            # I just made it a datetime so I can do timedelta operations on it. I iterate over every date in the date
            # range created earlier (dates) For each of these, I use range to get every offset available for each
            # timeslot, from 0 (no offset) to time_delta_mins (max offset) total_buffer is the combined time of the
            # length of each timeslot and the length of the breaks between the timeslots. I use this as the skip
            # parameter for range. This should create the timeslots with the appropriate time for the meeting and the
            # break time in between For every available offset, I make a tuple containing: The date The base plus the
            # offset The base plus the offset and the length of the meeting Thats all I can say about this horrible
            # thing Good luck
            timeslot_times = [
                [
                    (
                        date,
                        (base + datetime.timedelta(minutes=minute_offset)).time(),
                        (base + datetime.timedelta(minutes=minute_offset + length)).time()
                    )
                    for minute_offset in range(0, time_delta_mins, total_buffer)
                ]
                for date in dates
            ]

            # The resulting list will be a 2d list, with each list being the timeslots for one day.
            # Each list is a list of tuples with the following data:
            # Date, time_from, time_to
            flattened = sum(timeslot_times, [])

            objects = [
                TimeSlot(
                    schedule=schedule,
                    time_from=make_aware(datetime.datetime.combine(date, time_from)),
                    time_to=make_aware(datetime.datetime.combine(date, time_to)),
                    reservation_limit=form.cleaned_data["openings"],
                    is_locked=False,
                    auto_lock_after=make_aware(datetime.datetime.now() + datetime.timedelta(days=500000))
                ) for date, time_from, time_to in flattened
            ]

            TimeSlot.objects.bulk_create(objects)

        return redirect("schedule", schedule_id)

    return render(request, "app/pages/create_timeslots.html", {})


@require_http_methods(["GET", "POST"])
def reserve_timeslot(request, schedule_id, date, timeslot_id):
    schedule = Schedule.objects.filter(pk=schedule_id).get()
    timeslot = TimeSlot.objects.filter(pk=timeslot_id).get()
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
def view_reservations(request, schedule_id, date, timeslot_id):
    schedule = Schedule.objects.filter(pk=schedule_id).get()
    if schedule.owner.id != request.user.id:
        raise PermissionDenied()

    timeslot = TimeSlot.objects.filter(pk=timeslot_id).get()
    reservations = Reservation.objects.filter(timeslot=timeslot)

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
def view_schedule_reservations(request, schedule_id):
    schedule = Schedule.objects.filter(pk=schedule_id).get()
    if schedule.owner.id != request.user.id:
        raise PermissionDenied()

    if request.POST:
        # Just in case there will be more actions in the future.
        match request.POST["action"]:
            case "cancel":
                Reservation.objects.filter(pk=request.POST["id"]).delete()

    timeslots = TimeSlot.objects.filter(schedule=schedule)

    # This is the most bizarre bit of Python that I've ever written.
    reservations = sorted(
        {k: list(v) for k, v in groupby(
            list(
                filter(
                    lambda x: len(x["reservations"]) > 0 and x["timeslot"].time_from.date() >= datetime.date.today(),
                    [{"timeslot": t, "reservations": Reservation.objects.filter(timeslot=t)} for t in timeslots]
                )
            ),
            lambda x: x["timeslot"].time_from.date()
        )}.items()
    )

    return render(request, "app/pages/reservations_view_schedule.html",
                  {"schedule": schedule, "timeslots": reservations})


@require_http_methods(["GET"])
def reserve_confirmed(request):
    return render(request, "app/pages/reserve_confirmed.html", {

    })


def test(request, schedule):
    return HttpResponse(schedule.id)
