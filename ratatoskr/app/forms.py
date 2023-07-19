from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from .models import TimeSlot


class TimeslotGenerationForm(forms.Form):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    from_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}), required=True)
    to_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}), required=True)
    multiple_timeslots = forms.BooleanField(initial=False, required=False)
    timeslot_length = forms.IntegerField(required=False)
    timeslot_break = forms.IntegerField(required=False)
    openings = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('from_date')
        end_date = cleaned_data.get('to_date')
        start_time = cleaned_data.get('from_time')
        end_time = cleaned_data.get('to_time')
        
        errors = {}

        if start_date > end_date:
            errors['to_date'] = 'The End Date cannot be earlier than the Start Date'
        
        if start_time >= end_time:
            errors['to_time'] = 'The End Time cannot be earlier than the Start Time'

        if len(errors.keys()) > 0:
            raise forms.ValidationError(errors)

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
    name = forms.CharField(max_length=64)
    # should_lock_automatically = forms.BooleanField()
    auto_lock_after = forms.DateTimeField(required=False)
    visibility_select = forms.CharField(max_length=1)
    schedule_description = forms.CharField(max_length=1000)


class MessageForm(forms.Form):
    message = forms.CharField(max_length=8192)
    contact_info = forms.CharField(max_length=256)
    message_type = forms.CharField(max_length=256)
