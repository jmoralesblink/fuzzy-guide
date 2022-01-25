import secrets
import string

from django.conf import settings

from common_lib.cached_basic_auth_model_backend import CachedBasicAuthModelBackend
from common_lib.cli import prompt
from common_lib.service_enums import DeploymentEnvironments
from core.models import User

# cache the user, since a management command user will never change.  a new command will spin up a new instance
_management_command_user = None


def get_management_command_user() -> User:
    """
    Get the user running the management command, prompting the first time calling this.

    When running a management command, you aren't logged in, so it is not always easy or possible to get the user
    performing the action.  This will prompt the user to login, and after that initial prompt (which should be run
    at the start of the command), any future calls to get the user will get the cached value, with no prompting.

    For convenience, local development does not prompt, and just gets the initial user.
    """
    global _management_command_user

    # return the cached values, if we have them
    if _management_command_user:
        return _management_command_user

    # when running locally, just get the first user, as a convenience
    if settings.ENVIRONMENT == DeploymentEnvironments.local.value:
        return User.objects.get(id=1)

    # the first time calling this, get the username/password from the user
    username = prompt.get_str("Username")
    password = prompt.get_password("Password")

    # handle authentication, and getting the actual user object
    auth_backend = CachedBasicAuthModelBackend()
    _management_command_user = auth_backend.authenticate(request=None, username=username, password=password)
    if not _management_command_user or not _management_command_user.check_password(password):
        raise PermissionError("Invalid username or password")

    return _management_command_user


def create_user(
    first_name,
    last_name,
    is_superuser: bool,
    is_staff: bool,
    tenant_id: str,
    topic_name: str,
    user_name=None,
    email=None,
    password=None,
) -> (User, str):
    """
    Create a user, and setup related models and configurations
    :param first_name:
    :param last_name:
    :param is_superuser: Gives the user all permissions, but some code checks for groups, so they can't do everything
    :param is_staff: Allows the user to access the admin UI
    :param tenant_id: The tenant_id that the user is associated with
    :param user_name: The user name of the user.  Default to [first_name].[last_name] (all lower-case)
    :param email: The email address of the user.  Defaults to [username]@blinkhealth.com (all lower-case)
    :return: (user, password)
    """
    # setup calculated fields
    username = user_name or f"{first_name.lower()}.{last_name.lower()}"
    email = email or f"{username.lower()}@blinkhealth.com"
    password = password or generate_secure_password()

    # create the user
    new_user = User.objects.create_superuser(username=username, email=email, password=password)
    new_user.first_name = first_name
    new_user.last_name = last_name
    new_user.is_superuser = is_superuser
    new_user.is_staff = is_staff
    new_user.tenant_id = tenant_id
    new_user.topic_name = topic_name
    new_user.save()

    return new_user, password


def generate_secure_password(length: int = 12):
    alphabet = string.ascii_letters + string.digits + "!#$%&()=?*+|@{}[]"
    return "".join(secrets.choice(alphabet) for i in range(length))
