from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model

from common_lib.cli import prompt
from common_lib.errors import BlinkError
from core.constants import BLINK_TENANT_ID
from core.services import user_service

User = get_user_model()


@dataclass
class UserInfo:
    first_name: str
    last_name: str
    username: str  # lower case for RxOS, and upper case for Guardian
    email: str
    is_superuser: bool
    is_staff: bool  # whether they have access to the admin UI
    tenant_id: str
    topic_name: str
    password: str


def view_users():
    prompt.print_table_objects(list(User.objects.all()), ("id", "username", "first_name", "last_name"))


def create_user():
    user_info = _prompt_user_info()

    rxos_user, rxos_password = _create_user_instance(user_info)
    _print_new_user_info(rxos_user, rxos_password)


def _print_and_raise_error(message: str):
    prompt.print_error(message)
    raise BlinkError(message)


def _prompt_user_info() -> UserInfo:
    """Prompt the user for information about the user to create, and return it"""
    # get the user's name, and generate usernames
    first_name = prompt.get_str("First Name")
    last_name = prompt.get_str("Last Name")
    password = prompt.get_str("Password(leave empty for random secure password)")
    username = f"{first_name.lower()}.{last_name.lower()}"
    email = f"{username}@blinkhealth.com"
    topic_name = prompt.get_option("Topic Name", settings.TOPIC_CONFIG.keys())
    tenant_id = BLINK_TENANT_ID

    # ensure the email address is valid
    if not prompt.get_bool(f"Is the email address {username}@blinkhealth.com?"):
        email = prompt.get_str("Enter the email address")
        email_parts = email.split("@")
        if email_parts[1] != "blinkhealth.com":
            _print_and_raise_error(f"Invalid email domain: {email_parts[1]}")

    # ensure the user does not already exist
    if User.objects.filter(username=username).exists():
        _print_and_raise_error(f"User {username} already exists in RxOS")

    # check if they should be a super-user
    is_superuser = prompt.get_bool("Is the user a superuser?")

    # check if they need access to the admin UI
    is_staff = prompt.get_bool("Does the user need to access the admin UI?")

    return UserInfo(first_name, last_name, username, email, is_superuser, is_staff, tenant_id, topic_name, password)


def _create_user_instance(user_info: UserInfo) -> (User, str):
    user, password = user_service.create_user(
        user_info.first_name,
        user_info.last_name,
        is_superuser=user_info.is_superuser,
        is_staff=user_info.is_staff,
        tenant_id=user_info.tenant_id,
        topic_name=user_info.topic_name,
        user_name=user_info.username,
        email=user_info.email,
        password=user_info.password,
    )

    return user, password


def _print_new_user_info(user: User, password: str):
    prompt.print()
    prompt.print_success(f"User {user.username} created:")
    prompt.print_key_value_list(**{"Email": user.email, "Username": user.username, "Password": password})
