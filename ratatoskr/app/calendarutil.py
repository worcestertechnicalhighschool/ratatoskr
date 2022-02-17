
import base64
import uuid
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from allauth.socialaccount.models import SocialToken, SocialApp
from django.contrib.auth.models import User

from .models import Reservation, Schedule, ScheduleMeetingData, TimeSlot

# Notes:
# Client object is just a capsule for the Credentials, there is no cost to building multiple client objects

# Template strings for the IDs for each of our calendar elements
# The name+ID method for generating IDs for our calendar elements should be unique enough so it doesn't clash with any other IDs
# AutoIncrement fields in SQL never return previous numbers, so we should also be safe in that regard too.

CALENDAR_ID_PREFIX = base64.b32encode(bytearray("ratatoskr.techhigh.us", 'ascii')).decode('utf8') # e9gq8rbmdxtppwheehjp6u38d5kpgbknec
CALENDAR_SCHEDULE_ID = CALENDAR_ID_PREFIX + "{schedule_id}"
CALENDAR_TIMESLOT_EVENT_ID = CALENDAR_ID_PREFIX + "{timeslot_id}in{schedule_id}#"

def build_schedule_id(schedule: Schedule) -> str:
    return CALENDAR_SCHEDULE_ID % {
        "schedule_id": schedule.id
    }

def build_timeslot_event_id(timeslot: TimeSlot) -> str:
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

# Gets the calendar associated with the schedule
def create_calendar_for_schedule(schedule: Schedule) -> dict:
    client = build_calendar_client(schedule.owner)
    calendar_id = build_schedule_id(schedule)
    calendar_body = {
        'summary': f'Ratatoskr: {schedule.name}',
        'description': 'Calendar generated by Ratatoskr. Please do not delete.',
        'timeZone': 'America/New_York',
        'conferenceProperties': ["hangoutsMeet"],
        'id': calendar_id
    }
    dummy_event_body = {
        "summary": "Ratatoskr Dummy Event",
        "location": "Yggdrasil",
        "description": "This event was only supposed to exist for a short time. If this event happened to stay, you are free to delete it.",
        "start": {
            "dateTime": "1999-02-01T00:00:00-05:00",
            "timeZone": "America/New_York",
        },
        "end": {
            "dateTime": "1999-01-01T1:00:00-05:00",
            "timeZone": "America/New_York",
        },
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid5()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "attendees": [],
        "reminders": {"useDefault": False},
    }
    calendar = client.calendars().insert(body=calendar_body)
    # We are going to create a dummy event to get some conference data to use with other events on the same calendar
    event = calendar.events().insert(calendarId=calendar_id, body=dummy_event_body)
    conf_data = event["conferenceData"]
    ScheduleMeetingData.objects.create(
        schedule=schedule,
        meet_data=conf_data
    )
    # Delete the dummy event, we don't need it
    calendar.events().delete(calendarId=calendar_id, eventId=event["id"])

def update_schedule_events(schedule: Schedule):
    client = build_calendar_client(schedule.owner)
    