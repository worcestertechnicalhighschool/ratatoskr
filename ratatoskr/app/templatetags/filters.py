from django.template.defaultfilters import register


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
def last(l):
    return l[-1]
