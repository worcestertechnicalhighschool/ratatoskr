# Generated by Django 3.2.12 on 2022-03-16 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_rename_time_slot_reservation_timeslot'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
