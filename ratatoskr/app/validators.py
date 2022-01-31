from django import forms

class TimeslotGenerationForm(forms.Form):
    on_date = forms.DateField(validators=[])
    begin_time = forms.TimeField(validators=[])
    end_time = forms.TimeField(validators=[])
    timeslot_length = forms.IntegerField()
    timeslot_break = forms.IntegerField()
    openings = forms.IntegerField()
