import html
from django.template.defaultfilters import register
import re

from django.utils.html import strip_tags

from app.models import ScheduleSubscription
from app.models import Schedule

@register.filter
def addhour(t):
    mins = t.split(':')[1]
    hour = int(t.split(':')[0]) + 1
    if (hour > 23):
        hour = 0
    # zfill pads a string with 0's if it is < 9
    # example 2 returns "02," 13 returns "13"
    return f"{ str(hour).zfill(2) }:{mins}"



@register.filter
def index(l, i):
    return l[i]


@register.filter
def concatenate(arg1, arg2):
    return str(arg1) + str(arg2)


@register.filter
def available_count(timeslot):
    return timeslot.reservation_limit - len(timeslot.reservation_set.filter(confirmed=True))


@register.filter
def confirmed_count(timeslot):
    return len(timeslot.reservation_set.filter(confirmed=True))


@register.filter
def textified(html_data):
    text_only = re.sub('[ \t]+', ' ', strip_tags(html_data))
    return html.unescape(text_only.replace('\n ', '\n').strip())


@register.filter
def is_subscribed(schedule, user):
    return ScheduleSubscription.objects.filter(schedule=schedule.pk, user=user.pk).count() > 0


@register.filter
def is_guest(schedule, user):
    return ScheduleSubscription.objects.filter(schedule=schedule.pk, user=user.pk)[0].add_as_guest


@register.filter
def has_schedules(user):
    return Schedule.objects.filter(owner=user.pk).count() > 0


@register.filter
def last(l):
    return l[-1]

@register.filter
def is_student(request, user):
    return request.user.email.startswith("student.")


@register.filter
def is_teacher(request, user):
    return not request.user.email.startswith("student.") and request.user.email.endswith("worcesterschools.net")