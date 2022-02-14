from django import forms

class TimeslotGenerationForm(forms.Form):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    from_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}))
    to_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}))
    timeslot_length = forms.IntegerField()
    timeslot_break = forms.IntegerField()
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
    comment = forms.CharField(max_length=256)
    # TODO: Find out how to store phone numbers
    #phone = models.PhoneNumberField()

class ScheduleCreationForm(forms.Form):
    name = forms.CharField(max_length=64)
    should_lock_automatically = forms.BooleanField()
    auto_lock_after = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}), required=False)