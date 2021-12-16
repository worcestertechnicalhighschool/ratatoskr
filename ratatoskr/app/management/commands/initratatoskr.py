from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Sets up the server for a development environment'

    def handle(self, *args, **options):
        self.stdout.write("Migrating...")
        call_command("migrate")

        client_id = input("Client Id: ")
        client_secret = input("Client Secret: ")
        domain_name = input("Domain Name (leave blank for 127.0.0.1:8000): ")
        domain_display_name = input("Domain Display name (leave blank for 127.0.0.1:8000): ")

        x = Site.objects.get(pk=1).objects.first()

        x.domain = domain_name
        x.name = domain_display_name

        Site.objects.update(x)
        Site.save()

        SocialApp.objects.create(
            provider = "Google",
            name = "ratatoskr",
            client_id = client_id,
            secret_key = client_secret,
            sites = [x]
        )
        SocialApp.save()
