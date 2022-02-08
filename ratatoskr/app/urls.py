from datetime import datetime
from django.urls import path

from . import views
from . import converters

urlpatterns = [
    path('', views.index, name='index'),
    path('schedules/', views.view_self_schedules, name='view-schedules'),
    path('create-schedule/', views.create_schedule, name='create-schedule'),
    path('upcoming/', views.upcoming_meetings, name='upcoming-meetings'),
    path('help/', views.help_page, name='help'),
    path('settings/', views.settings, name='settings'),
    path('schedule/<int:schedule_id>', views.schedule, name='schedule'),
    path('schedule/<int:schedule_id>/edit', views.schedule_edit, name='schedule-edit'),
    path('schedule/<int:schedule_id>/<datetime:date>', views.schedule_day, name='schedule-day'),
    path('schedule/<int:schedule_id>/create-timeslots', views.create_timeslots, name='create-timeslots'),
    path('schedule/<int:schedule_id>/<datetime:date>/reserve/<int:timeslot_id>', views.reserve_timeslot, name='reserve-timeslot'),
    path('schedule/reservation-confirmed', views.reserve_confirmed, name='reserve-confirmed'),
]
