from django.template.defaulttags import register

@register.inclusion_tag("app/components/test.html")
def TestComponent(echo):
    return {
        "echo": echo
    }
