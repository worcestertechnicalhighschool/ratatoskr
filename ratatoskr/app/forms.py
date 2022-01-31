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
