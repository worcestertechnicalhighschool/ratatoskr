# Generated by Django 4.1.7 on 2023-03-20 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_delete_historicalschedule'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalreservation',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical reservation', 'verbose_name_plural': 'historical reservations'},
        ),
        migrations.AlterModelOptions(
            name='historicalschedulesubscription',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical schedule subscription', 'verbose_name_plural': 'historical schedule subscriptions'},
        ),
        migrations.AlterField(
            model_name='historicalreservation',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalschedulesubscription',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]
