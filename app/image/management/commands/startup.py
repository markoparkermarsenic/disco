from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from image.models import Plan, Subscriber


class Command(BaseCommand):
    help = "Load some inital states for User, and Plan"

    def handle(self, *args, **options):
        try:
            # Check if the default Plan exists in the database
            basic, created = Plan.objects.get_or_create(
                name="Basic",
                thumbnail_sizes=[[200, 200]],
                expiring_links=True,
                original_image=False,
            )
            print("created BASIC")
            premium, created = Plan.objects.get_or_create(
                name="Premium",
                thumbnail_sizes=[[200, 200], [400, 400]],
                expiring_links=False,
                original_image=True,
            )
            enterprise, created = Plan.objects.get_or_create(
                name="Enterprise",
                thumbnail_sizes=[[200, 200], [400, 400]],
                expiring_links=True,
                original_image=True,
            )
            print("created PLANS")

            # Check if the default User exists in the database
            dev_user, created = User.objects.get_or_create(
                username="dev",
                password="mypass",
            )
            print("created dev user")
            # Check if the default Subscriber exists in the database
            subscriber, created = Subscriber.objects.get_or_create(
                user=dev_user, plan=enterprise
            )
            print("created subscriber profile")

        except:
            CommandError("failed")
