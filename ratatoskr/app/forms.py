import datetime
from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from .models import TimeSlot
from django.utils import timezone, dateformat

class TimeslotGenerationForm(forms.Form):
    # This bit takes the current UTC time, 
    # rounds to the nearest half hour,
    # Then localizes it to localtime + 1 hour
    # This allows the form to render with a good starting time for users.
    utc_time = timezone.now()
    mins = utc_time.minute
    rounded_mins = 30 * round(mins / 30)
    if rounded_mins > 30:
        rounded_mins = 0
    nearest_utc_time = utc_time.replace(minute=rounded_mins, second=0, microsecond=0)
    best_start_date = dateformat.format(nearest_utc_time - datetime.timedelta(hours=3), 'Y-m-d')
    best_end_date = dateformat.format(nearest_utc_time - datetime.timedelta(hours=2), 'Y-m-d')
    best_start_time = dateformat.format(nearest_utc_time - datetime.timedelta(hours=3), 'H:i')
    best_end_time = dateformat.format(nearest_utc_time - datetime.timedelta(hours=2), 'H:i')

    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=best_start_date, required=True)
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=best_end_date)
    from_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}), initial=best_start_time, required=True)
    to_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}), initial=best_end_time, required=True)
    attendees = forms.IntegerField(initial=1, label="Number of Attendees")

    multiple_timeslots = forms.BooleanField(
        initial=False, 
        required=False, 
        widget=forms.CheckboxInput(
            attrs={
                "role": "switch",
            }
        )
    )

    timeslot_length = forms.IntegerField(required=False)
    timeslot_break = forms.IntegerField(required=False)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('from_date')
        end_date = cleaned_data.get('to_date')
        start_time = cleaned_data.get('from_time')
        end_time = cleaned_data.get('to_time')
        attendees = cleaned_data.get('attendees')
        # vars for validation
        current_time = timezone.now() - datetime.timedelta(hours=4)
        today = timezone.now() - datetime.timedelta(hours=4)
        
        errors = {}

        if start_date < datetime.date.today():
            errors['from_date'] = 'The start date cannot be in the past'

        if start_date > end_date:
            errors['to_date'] = 'The End Date cannot be earlier than the Start Date'

        if start_date <= datetime.date.today() and start_time < current_time.time():
            errors['from_time'] = 'The start time cannot be in the past'

        if start_time >= end_time:
            errors['to_time'] = 'The End Time cannot be earlier than the Start Time'
        
        if attendees < 1:
            errors['attendees'] = 'You must allow at least 1 attendee'

        print(len(errors.keys()))
        if len(errors.keys()) > 0:
            raise forms.ValidationError(errors)

        # print(cleaned_data)
        return cleaned_data


class ReservationForm(forms.Form):
    name = forms.CharField(max_length=747)
    email = forms.EmailField()
    comment = forms.CharField(max_length=256, initial="", required=False)
    # TODO: Find out how to store phone numbers
    # phone = models.PhoneNumberField()


class CopyTimeslotsForm(forms.Form):
    action = forms.CharField(max_length=4)
    timeslots = forms.CharField(max_length=500)
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}))

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["timeslots"] = list(
            map(lambda x: TimeSlot.objects.get(pk=int(x)), cleaned_data["timeslots"].split(",")))
        return cleaned_data


class ScheduleCreationForm(forms.Form):
    name = forms.CharField(max_length=64, label="Event name")
    schedule_description = forms.CharField(max_length=1000, widget=forms.Textarea())
    # should_lock_automatically = forms.BooleanField()
    # auto_lock_after = forms.DateTimeField(required=False)
    VISIBILITY_CHOICES = [
        ('A', 'Public'),
        ('U', 'Unlisted'),
        ('P', 'Private'),
    ]
    visibility_select = forms.ChoiceField(choices=VISIBILITY_CHOICES)


class MessageForm(forms.Form):
    message = forms.CharField(max_length=8192)
    contact_info = forms.CharField(max_length=256)
    message_type = forms.CharField(max_length=256)
