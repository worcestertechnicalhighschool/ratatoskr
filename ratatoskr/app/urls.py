from datetime import datetime
from django.urls import path

from . import views
from . import converters

urlpatterns = [
    path('', views.index, name='index'),
    path('create-schedule/', views.create_schedule, name='create-schedule'),
    path('schedule/<int:schedule_id>', views.schedule, name='schedule'),
    path('schedule/<int:schedule_id>/delete', views.schedule_delete, name='schedule-delete'),
    path('schedule/<int:schedule_id>/lock', views.schedule_lock, name='schedule-lock'),
    path('schedule/<int:schedule_id>/<datetime:date>', views.schedule_day, name='schedule-day'),
    path('schedule/<int:schedule_id>/create-timeslots', views.create_timeslots, name='create-timeslots'),
]
