from email.message import EmailMessage
from django.core.mail import EmailMultiAlternatives, send_mail, send_mass_mail
from django.template.loader import get_template
from django.contrib.sites.models import Site
from ratatoskr.threadutil import threadpool_decorator

from ratatoskr.settings import SITE_ID

pool = threadpool_decorator(2) # we dont need that many threads

@pool
def send_confirmation_email(reservation):
    html_content = get_template("email/emails/confirm_reservation.html")
    txt_content = get_template("email/emails/confirm_reservation.txt")

    ctx = {
        "reservation": reservation,
        "timeslot": reservation.timeslot,
        "schedule": reservation.timeslot.schedule,
        "site": Site.objects.get(pk=SITE_ID)
    }
    send_mail(
        subject=f"Ratatoskr: Confirm reservation for {reservation.timeslot.schedule.name}",
        html_message=html_content.render(ctx),
        message=txt_content.render(ctx),
        from_email="ratatoskr@techhigh.us",
        recipient_list=[reservation.email]
    )

@pool
def send_success_email(reservation):
    html_content = get_template("email/emails/reservation_success.html")
    txt_content = get_template("email/emails/reservation_success.txt")

    ctx = {
        "reservation": reservation,
        "timeslot": reservation.timeslot,
        "schedule": reservation.timeslot.schedule,
        "site": Site.objects.get(pk=SITE_ID)
    }
    send_mail(
        subject=f"Ratatoskr: Successfully confirmed reservation for {reservation.timeslot.schedule.name}",
        html_message=html_content.render(ctx),
        message=txt_content.render(ctx),
        from_email="ratatoskr@techhigh.us",
        recipient_list=[reservation.email]
    )

@pool
def send_cancelled_email(reservation):
    html_content = get_template("email/emails/cancelled_reservation.html")
    txt_content = get_template("email/emails/cancelled_reservation.txt")

    ctx = {
        "reservation": reservation,
        "timeslot": reservation.timeslot,
        "schedule": reservation.timeslot.schedule,
        "site": Site.objects.get(pk=SITE_ID)
    }
    send_mail(
        subject=f"Ratatoskr: Cancelled reservation on {reservation.timeslot.schedule.name}",
        html_message=html_content.render(ctx),
        message=txt_content.render(ctx),
        from_email="ratatoskr@techhigh.us",
        recipient_list=[reservation.email]
    )

def send_change_email(reservation, action):
    html_content = get_template("email/emails/schedule_change.html")
    txt_content = get_template("email/emails/schedule_change.txt")

    ctx = {
        "reservation": reservation,
        "timeslot": reservation.timeslot,
        "schedule": reservation.timeslot.schedule,
        "site": Site.objects.get(pk=SITE_ID),
        "action": action
    }

    from .models import ScheduleSubscription  # Avoiding circular import.
    subscribers = [i.user for i in ScheduleSubscription.objects.filter(schedule=reservation.timeslot.schedule.pk)]

    @pool
    def inner():
        nonlocal ctx
        ctx = ctx | { "name": reservation.timeslot.schedule.owner.get_full_name }
        pass
        send_mail(
            subject=f"Ratatoskr: Reservation {action}ed on {reservation.timeslot.schedule.name}",
            html_message=html_content.render(ctx),
            message=txt_content.render(ctx),
            from_email="ratatoskr@techhigh.us",
            recipient_list=[reservation.timeslot.schedule.owner.email]
        )
    inner()

    ctx = ctx | { "is_subscriber": True }
    @pool
    def inner():
        nonlocal ctx
        for sub in subscribers:
            ctx = ctx | { "name": sub.get_full_name }
            send_mail(
                subject=f"Ratatoskr: Reservation {action}ed on {reservation.timeslot.schedule.name}",
                html_message=html_content.render(ctx),
                message=txt_content.render(ctx),
                from_email="ratatoskr@techhigh.us",
                recipient_list=[sub.email]
            )
    inner()
