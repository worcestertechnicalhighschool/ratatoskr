from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import get_template
from django.contrib.sites.models import Site

from ratatoskr.settings import SITE_ID


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
        subject=f"Ratatoskr: Confirm reservation for f{reservation.timeslot.schedule.name}",
        html_message=html_content.render(ctx),
        message=txt_content.render(ctx),
        from_email="ratatoskr@techhigh.us",
        recipient_list=[reservation.email]
    )


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
    send_mail(
        subject=f"Ratatoskr: Reservation {action}ed on {reservation.timeslot.schedule.name}",
        html_message=html_content.render(ctx),
        message=txt_content.render(ctx),
        from_email="ratatoskr@techhigh.us",
        recipient_list=[reservation.email]
    )