from django import forms

class TimeslotGenerationForm(forms.Form):
    on_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    begin_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}))
    timeslot_length = forms.IntegerField()
    timeslot_break = forms.IntegerField()
    openings = forms.IntegerField()
