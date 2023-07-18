from datetime import datetime
from django.urls import path

from . import views
from . import converters

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('subscriptions/', views.view_subscriptions, name='view-subscriptions'),
    path('schedule/create', views.create_schedule, name='create-schedule'),
    path('schedule/<schedule:schedule>', views.schedule, name='schedule'),
    path('schedule/<schedule:schedule>/edit', views.edit_schedule, name='edit-schedule'),
    path('schedule/<schedule:schedule>/copy', views.copy_timeslots, name='copy-timeslots'),
    path('schedule/<schedule:schedule>/subscription', views.subscribe_schedule, name='subscription'),
    path('schedule/<schedule:schedule>/reservations', views.view_schedule_reservations, name='view-schedule-reservations'),
    path('schedule/<schedule:schedule>/create-timeslots', views.create_timeslots, name='create-timeslots'),
    path('schedule/<schedule:schedule>/<datetime:date>', views.schedule_day, name='schedule-day'),
    path('schedule/<schedule:schedule>/<datetime:date>/reserve/<timeslot:timeslot>', views.reserve_timeslot, name='reserve-timeslot'),
    path('schedule/<schedule:schedule>/<datetime:date>/view/<timeslot:timeslot>', views.view_reservations, name='view-reservations'),
    path('reservation/find', views.find_reservation, name='find-reservation'),
    path('reservation/<reservation:reservation>/confirm', views.confirm_reservation, name='confirm-reservation'),
    path('reservation/<reservation:reservation>/cancel', views.cancel_reservation, name='cancel-reservation'),
    path('schedule/reservation-confirmed', views.reserve_confirmed, name='reserve-confirmed'),
    path('schedules/<int:user_id>', views.user_schedules, name='user-schedules'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help_page, name='help'),
    path('robots.txt', views.robots, name='robots'),
    path('privacy/', views.privacy, name='privacy'),
    path('form-error/', views.form_error, name='form-error'),
    
]
