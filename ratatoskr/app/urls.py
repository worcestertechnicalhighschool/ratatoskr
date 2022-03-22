from datetime import datetime
from django.urls import path

from . import views
from . import converters

urlpatterns = [
    path('', views.index, name='index'),
    path('create-schedule/', views.create_schedule, name='create-schedule'),
    path('schedule/<schedule:schedule>', views.schedule, name='schedule'),
    path('schedule/<schedule:schedule>/edit', views.schedule_edit, name='schedule-edit'),
    path('schedule/<schedule:schedule>/reservations', views.view_schedule_reservations, name='view-schedule-reservations'),
    path('schedule/<schedule:schedule>/<datetime:date>', views.schedule_day, name='schedule-day'),
    path('schedule/<schedule:schedule>/create-timeslots', views.create_timeslots, name='create-timeslots'),
    path('schedule/<schedule:schedule>/<datetime:date>/reserve/<timeslot:timeslot>', views.reserve_timeslot, name='reserve-timeslot'),
    path('schedule/<schedule:schedule>/<datetime:date>/view/<timeslot:timeslot>', views.view_reservations, name='view-reservations'),
    path('reservation/<reservation:reservation>/confirm', views.confirm_reservation, name='confirm-reservation'),
    path('reservation/<reservation:reservation>/cancel', views.cancel_reservation, name='cancel-reservation'),
    path('schedule/reservation-confirmed', views.reserve_confirmed, name='reserve-confirmed'),
    path('schedules/<int:user_id>', views.user_schedules, name='user-schedules'),
    path('mail/', views.test)
]
