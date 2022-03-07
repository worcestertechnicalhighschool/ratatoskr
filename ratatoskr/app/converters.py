from pyexpat import model
from django.urls import register_converter
from django.db import models
from datetime import datetime

from .models import Schedule

class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value

# Converter class factory for creating URL converter classes
DIGIT_REGEX = "\d+"
def create_model_converter(model_class: models.Model, regex: str = DIGIT_REGEX):
    regex = regex
    class Converter:
        regex = regex

        def to_python(self, value):
            return model_class.objects.get(pk=int(value))

        def to_url(self, value):
            return value
    
    return Converter

register_converter(DateConverter, 'datetime')
register_converter(create_model_converter(Schedule), 'schedule')
