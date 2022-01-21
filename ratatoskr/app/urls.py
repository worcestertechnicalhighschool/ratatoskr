from datetime import datetime
from django.urls import path, register_converter

from . import views

class DateConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value

register_converter(DateConverter, 'datetime')

urlpatterns = [
    path('', views.index, name='index'),
    path('create-schedule/', views.create_schedule, name='create-schedule'),
    path('schedule/<int:schedule_id>', views.schedule, name='schedule'),
    path('schedule/<int:schedule_id>/<datetime:date>', views.schedule_day, name='schedule-day'),
]
