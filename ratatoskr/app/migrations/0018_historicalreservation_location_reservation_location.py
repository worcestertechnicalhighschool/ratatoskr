# Generated by Django 4.2.1 on 2023-07-19 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_alter_historicalreservation_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreservation',
            name='location',
            field=models.CharField(default='Remote', max_length=1024),
        ),
        migrations.AddField(
            model_name='reservation',
            name='location',
            field=models.CharField(default='Remote', max_length=1024),
        ),
    ]
