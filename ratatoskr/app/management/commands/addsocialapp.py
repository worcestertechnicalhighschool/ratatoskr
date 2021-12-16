from allauth.socialaccount import providers
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Helper for adding a social application. Handy if you don\'t like going clicky clicky!'

    def handle(self, *args, **options):
        self.stdout.write("Migrating...")
        call_command("migrate")
        
        # Get all the needed information
        # Google secrets
        client_id = input("Client Id: ")
        client_secret = input("Client Secret: ")

        # Domain name (needed for google)
        # The ternary if statements are defaults for developer convinence
        domain_name = input("Domain Name (leave blank for 127.0.0.1:8000): ")
        domain_name = domain_name if domain_name != "" else "127.0.0.1:8000"

        domain_display_name = input("Domain Display Name (leave blank for 127.0.0.1:8000): ")
        domain_name = domain_name if domain_name != "" else "127.0.0.1:8000"

        # Take the default site object and change the domain name
        site = Site.objects.get(pk=1)

        site.domain = domain_name
        site.name = domain_display_name

        site.save()
        
        # Register the SocialApp instance
        app = SocialApp.objects.create(
            provider = "google",
            name = "ratatoskr",
            client_id = client_id,
            secret = client_secret,
        )

        app.save()

        app.sites.add(site)

        app.save()
