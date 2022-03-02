from django import forms
from django.contrib.postgres.forms import SimpleArrayField


class TimeslotGenerationForm(forms.Form):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    from_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}))
    to_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}))
    multiple_timeslots = forms.BooleanField(initial=False, required=False)
    timeslot_length = forms.IntegerField(required=False)
    timeslot_break = forms.IntegerField(required=False)
    openings = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        # st = cleaned_data['from_time']
        # end = cleaned_data['to_time']
        # if st > end :
        #      raise forms.ValidationError('The start time must be earlier than the end time.')
        return cleaned_data


class ReservationForm(forms.Form):
    name = forms.CharField(max_length=747)
    email = forms.EmailField()
    comment = forms.CharField(max_length=256, initial="", required=False)
    # TODO: Find out how to store phone numbers
    # phone = models.PhoneNumberField()


class ScheduleCreationForm(forms.Form):
    name = forms.CharField(max_length=64)
    should_lock_automatically = forms.BooleanField()
    auto_lock_after = forms.TimeField(widget=forms.DateTimeInput(attrs={'type': 'time'}), required=False)
