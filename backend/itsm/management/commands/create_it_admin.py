from getpass import getpass

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.password_validation import validate_password

from itsm.models import User


class Command(BaseCommand):
    help = "Create an IT administrator account interactively."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        if User.objects.filter(username=username).exists():
            raise CommandError("A user with that username already exists.")

        password = getpass("New IT administrator password: ")
        confirmation = getpass("Confirm password: ")
        if password != confirmation:
            raise CommandError("The passwords did not match.")

        user = User(username=username, email=email, role="it_admin", is_staff=True)
        try:
            validate_password(password, user)
        except Exception as error:
            raise CommandError(str(error)) from error

        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"IT administrator '{username}' created."))
