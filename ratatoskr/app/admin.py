from django.contrib import admin
from .models import Reservation, Schedule, TimeSlot

# Register your models here.

class ReservationInline(admin.TabularInline):
    model = Reservation
class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
class TimeSlotAdmin(admin.ModelAdmin):
    inlines = [ReservationInline]
class ScheduleAdmin(admin.ModelAdmin):
    inlines = [TimeSlotInline]

admin.site.register(TimeSlot, TimeSlotAdmin)
admin.site.register(Reservation)
admin.site.register(Schedule, ScheduleAdmin)