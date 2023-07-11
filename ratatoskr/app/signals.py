from allauth.account.signals import user_logged_in as allauth_user_logged_in
from django.contrib.auth import logout 
from django.contrib import messages
from ratatoskr.settings import DEBUG

# TODO: Find a way to not have the default login message pop up

@allauth_user_logged_in.connect
def give_staff_permission_if_staff_in_worceterschools_domain(request, user, **kwargs):
    # You may pass 😎
    if user.is_staff or user.is_superuser:
        return

    email_user, email_domain = user.email.split("@")

    if email_domain not in ("worcesterschools.net", "techhigh.us"):
        messages.error(request, "Only teacher accounts registered within the `worcesterschools` domain are allowed to login")
        if not DEBUG:
            logout(request)

    if email_user.startswith("student.") and email_domain == "worcesterschools.net":
        messages.error(request, "Students are not allowed to login unless given permission by site maintainers")
        if not DEBUG:
            logout(request)
    if DEBUG:
        messages.info(request, "But since you are in DEBUG mode, you can log in anyways")