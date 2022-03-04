from django.template.defaultfilters import register


@register.filter
def index(l, i):
    return l[i]


@register.filter
def concatenate(arg1, arg2):
    return str(arg1) + str(arg2)


@register.filter
def last(l):
    return l[-1]
