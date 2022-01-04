from django.template.defaulttags import register

@register.inclusion_tag("app/components/test.html")
def test_component(echo):
    return {
        "echo": echo
    }
