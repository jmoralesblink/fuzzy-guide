import logging

from django.conf import settings
from django.core.management import BaseCommand

from common_lib.cli.utils import command_tree
from common_lib.service_enums import DeploymentEnvironments
from core.services.user_service import get_management_command_user
from django_service_bootstrap.management.commands.ops_tool_impl import user_management, messaging_management

_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    root_commands = {
        "Widget Management": {"Find Invalid Widgets": lambda: print("Find invalid wdigets")},
        "Messaging Management": {"Manage DLQ": messaging_management.manage_dlq},
        "User Management": {
            "View Users": user_management.view_users,
            "Create User": user_management.create_user,
            "Reset Password": lambda: print("Reset Password"),
        },
        "System Management": {"Check System Health": lambda: print("Check System Health")},
    }

    def handle(self, *args, **options):
        # require the user to login before being able to use the ops tool (logs in automatically when run locally)
        get_management_command_user()

        # present the user with a list of commands to run
        command_tree(self.root_commands)
