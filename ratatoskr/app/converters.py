from pyexpat import model
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.urls import register_converter
from django.db import models
from datetime import datetime

from .models import Reservation, Schedule, TimeSlot


class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value


# Converter class factory for creating URL converter classes
DIGIT_REGEX = "\d+"


def create_model_converter(model_class: models.Model, regex: str = DIGIT_REGEX):
    class Converter:
        def __init__(self):
            self.regex = regex

        def to_python(self, value):
            try:
                return model_class.objects.get(pk=value)
            except ObjectDoesNotExist as e:
                raise Http404 from e

        def to_url(self, value):
            return value

    return Converter


register_converter(DateConverter, 'datetime')
register_converter(create_model_converter(Schedule), 'schedule')
register_converter(create_model_converter(TimeSlot), 'timeslot')
register_converter(create_model_converter(Reservation), 'reservation')
