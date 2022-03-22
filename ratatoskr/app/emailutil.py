from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import get_template
from django.contrib.sites.models import Site

from ratatoskr.settings import SITE_ID

def send_confirmation_email(reservation):
    html_content = get_template("email/emails/confirm_reservation.html")
    txt_content = get_template("email/emails/alt/confirm_reservation.txt")

    ctx = {
        "reservation": reservation,
        "site": Site.objects.get(pk=SITE_ID)
    }
    send_mail(
        subject="Ratatoskr",
        html_message=html_content.render(ctx),
        message=txt_content.render(ctx),
        from_email="ratatoskr@techhigh.us",
        recipient_list=[reservation.email]
    )