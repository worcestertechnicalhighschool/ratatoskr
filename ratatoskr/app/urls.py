from datetime import datetime
from django.urls import path

from . import views
from . import converters

urlpatterns = [
    path('', views.index, name='index'),
    path('create-schedule/', views.create_schedule, name='create-schedule'),
    path('schedule/<int:schedule_id>', views.schedule, name='schedule'),
    path('schedule/<int:schedule_id>/edit', views.schedule_edit, name='schedule-edit'),
    path('schedule/<int:schedule_id>/reservations', views.view_schedule_reservations, name='view-schedule-reservations'),
    path('schedule/<int:schedule_id>/<datetime:date>', views.schedule_day, name='schedule-day'),
    path('schedule/<int:schedule_id>/create-timeslots', views.create_timeslots, name='create-timeslots'),
    path('schedule/<int:schedule_id>/<datetime:date>/reserve/<int:timeslot_id>', views.reserve_timeslot, name='reserve-timeslot'),
    path('schedule/<int:schedule_id>/<datetime:date>/view/<int:timeslot_id>', views.view_reservations, name='view-reservations'),
    path('schedule/reservation-confirmed', views.reserve_confirmed, name='reserve-confirmed'),
    path('schedules/<int:user_id>', views.user_schedules, name='user-schedules'),
    path('mail', views.test)
]
