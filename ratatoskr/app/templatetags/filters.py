from django.template.defaultfilters import register

@register.filter
def index(l, i):
    return l[i]
