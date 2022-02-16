from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from allauth.socialaccount.models import SocialToken, SocialApp
from django.contrib.auth.models import User

from .models import Reservation, Schedule, TimeSlot

# Notes:
# Client object is just a capsule for the Credentials, there is no cost to building multiple client objects

# Template strings for the IDs for each of our calendar elements
# The ID+DomainName method for generating IDs for our calendar elements should be unique enough so it doesn't clash with any other IDs
# AutoIncrement fields in SQL never return previous numbers, so we should also be safe in that regard too.

CALENDAR_ID_SUFFIX = "ratatoskr.techhigh.us"
CALENDAR_SCHEDULE_ID = "{schedule_id}#" + CALENDAR_ID_SUFFIX                        # Ex: "9824#ratatoskr.techhigh.us"
CALENDAR_TIMESLOT_EVENT_ID = "{timeslot_id}@{schedule_id}#" + CALENDAR_ID_SUFFIX    # Ex: "74343@9824#ratatoskr.techhigh.us"

def make_schedule_id(schedule: Schedule) -> str:
    return CALENDAR_SCHEDULE_ID % {
        "schedule_id": schedule.id
    }

def make_timeslot_event_id(timeslot: TimeSlot) -> str:
    return CALENDAR_TIMESLOT_EVENT_ID % {
        "schedule_id": timeslot.id,
        "timeslot_id": timeslot.schedule.id
    }

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
    
