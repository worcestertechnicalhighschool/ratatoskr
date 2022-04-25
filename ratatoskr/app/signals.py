from cmath import log
import re
# from django.contrib.auth.signals import user_logged_in
from allauth.account.signals import user_logged_in
from django.contrib.auth import logout 
from django.contrib import messages
from ratatoskr.settings import DEBUG


@user_logged_in.connect
def give_staff_permission_if_staff_in_worceterschools_domain(request, user, **kwargs):

    # You may pass 😎
    if user.is_staff or user.is_superuser:
        return
    
    email_user, email_domain = user.email.split("@")

    if email_domain not in ("worcesterschools.net", "techhigh.us"):
        messages.add_message(request, messages.INFO, "Only Google accounts registered within the `worcesterschools` domain are allowed to login")
        if not DEBUG:
            logout(request)

    if email_user.startswith("student.") and email_domain == "worcesterschools.net":
        messages.add_message(request, messages.INFO, "Students are not allowed to login unless given permission by site maintainers")
        if not DEBUG:
            logout(request)
    

