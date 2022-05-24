import os
from allauth.socialaccount import providers
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Helper for registering a social application. Handy if you don\'t like going clicky clicky!'

    def add_arguments(self, parser) -> None:
        parser.add_argument("-c", "--config", action="store_true")
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        override_socialapp = False

        # -c get from environment variables
        if options['config']:
            app = SocialApp(
                provider = "google",
                name = "ratatoskr",
                client_id = os.environ["GOOGLE_CLIENT_ID"],
                secret = os.environ["GOOGLE_CLIENT_SECRET"],
            )

            site = Site.objects.get(pk=1)

            site.domain = os.environ["SITE_URL"]
            site.name = os.environ["SITE_URL"]

            site.save()

            app.save()

            return

        # In the case we already have another social app
        if SocialApp.objects.count() == 1:
            self.stdout.write("SocialApp instance found.")
            res = input("Would you like to override it? (overriding does not happen until end) (y/N) ")
            if res.lower() != "y":
                self.stdout.write("Aborting...")
                return
            # Real risky, dude...
            override_socialapp = True
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
        domain_display_name = domain_display_name if domain_display_name != "" else "127.0.0.1:8000"

        self.stdout.write(f"""
        {client_id=}
        {client_secret=}
        {domain_name=}
        {domain_display_name=}
        """)

        conf = input("Does this look right to you? (y/N): ")
        if conf.lower() != "y":
            self.stdout.write("Aborting...")
            return

        if override_socialapp:
            self.stdout.write("Deleting SocialApp model...")
            SocialApp.objects.all().delete()


        self.stdout.write("Writing Site model...")
        # Take the default site object and change the domain name
        site = Site.objects.get(pk=1)

        site.domain = domain_name
        site.name = domain_display_name

        site.save()
        
        self.stdout.write("Writing SocialApp model...")
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

        self.stdout.write("All done, partner!")
