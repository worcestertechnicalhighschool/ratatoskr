import html
from django.template.defaultfilters import register
import re

from django.utils.html import strip_tags

from app.models import ScheduleSubscription


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
def last(l):
    return l[-1]
