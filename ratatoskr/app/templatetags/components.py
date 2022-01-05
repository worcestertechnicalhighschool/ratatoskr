from django.template.defaulttags import register

@register.inclusion_tag("app/components/test.html")
def test_component(echo):
    return {
        "echo": echo
    }

@register.inclusion_tag("app/components/login_button.html")
def login_button():
    return {}