from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from allauth.socialaccount.models import SocialToken, SocialApp
from django.contrib.auth.models import User

def build_calendar_api(user: User):
    token = SocialToken.objects.get(account__user=user, account__provider='google')
    google_app = SocialApp.objects.get(provider="google")
    credentials = Credentials(
        token=token.token,
        refresh_token=token.token_secret,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=google_app.client_id, 
        client_secret=google_app.secret) 
    return build('calendar', 'v3', credentials=credentials)
