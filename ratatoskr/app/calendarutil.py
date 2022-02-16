from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from allauth.socialaccount.models import SocialToken, SocialApp
from django.contrib.auth.models import User

from .models import Reservation, TimeSlot

# Builds the calendar api using the User's api tokens
def build_calendar_client(user: User):
    token = SocialToken.objects.get(account__user=user, account__provider='google')
    google_app = SocialApp.objects.get(provider="google")
    credentials = Credentials(
        token=token.token,
        refresh_token=token.token_secret,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=google_app.client_id, 
        client_secret=google_app.secret) 
    return build('calendar', 'v3', credentials=credentials)

def update_user(timeslot: TimeSlot) -> None:
    schedule = timeslot.schedule
    owner = schedule.owner
    client = build_calendar_client(owner)
    event = {
        'summary': 'Ratatoskr: Meeting Reservation',
        'location': 'Remote',
        'description': '',
        'start': {
            'dateTime': timeslot.time_from.isoformat(),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': timeslot.time_to.isoformat(),
            'timeZone': 'America/New_York',
        },
        'attendees': [{'email': t.email} for t in timeslot.reservation_set],
        'reminders': {
            'useDefault': True
        },
    }
    
