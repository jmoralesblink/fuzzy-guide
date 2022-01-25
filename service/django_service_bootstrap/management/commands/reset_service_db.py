from django.contrib.auth import get_user_model
from django.core import management
from django.core.management.base import BaseCommand
from django.db import connection

from core.constants import BLINK_TENANT_ID


class Command(BaseCommand):
    help = "Reset the db and load in base fixture data"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email to use as login (should be blinkhealth.com)")
        # parser.add_argument("--no_users", action="store_true", required=False, help="Don't load users.json")

    def handle(self, *args, **options):
        # load_users = not options["no_users"]
        email = options["email"]
        username = email.split("@")[0]
        name = username.split(".")
        first_name = name[0]
        last_name = name[1] if len(name) > 1 else "last_name"

        database_host_name: str = connection.settings_dict["HOST"]
        database_name: str = connection.settings_dict["NAME"]

        print(f"Resetting backend database: {database_name} on {database_host_name}")

        # Wipe database
        management.call_command("reset_db")
        management.call_command("migrate")
        # Make superuser
        User = get_user_model()
        new_user = User.objects.create_superuser(
            username=username,
            email=email,
            password="password",
            tenant_id=BLINK_TENANT_ID,
            topic_name="rxos_general_queue",
        )
        if new_user is None:
            print("had to get the user")
            new_user = User.objects.get(username=username)

        # set a first and last name, so we can get initials when doing things like PV1
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()

        # Initialize database
        # management.call_command("loaddata", "users", "initial")
        # can add app_label='core' to specify a specific app to load from, otherwise it will check all apps
        # management.call_command("loaddata", "initial")

        # create user for that will be used by RxOS backend to invoke Django Service Bootstrap.
        User.objects.create_superuser(
            username="rxos_local",
            email="rxos@blinkhealth.com",
            password="rxos_local",
            tenant_id=BLINK_TENANT_ID,
            topic_name="rxos_general_queue",
        )
