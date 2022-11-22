from allauth.account.signals import user_logged_in as allauth_user_logged_in
from django.contrib.auth import logout 
from django.contrib import messages
from ratatoskr.settings import DEBUG
    