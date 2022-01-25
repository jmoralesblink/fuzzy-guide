import binascii
import hashlib
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from blink_logging_metrics.metrics import statsd
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.timezone import make_aware

HASH_ITERATIONS = 100
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 60

_logger = logging.getLogger(__name__)
# if true, return the cached user object for each request, instead of re-loading from the DB each time
# this saves a DB call for each request, but requires that your code never changes the user model
_return_cached_user = (
    settings.CACHED_BASIC_AUTH_MODEL_BACKEND.get("return_cached_user_object", False)
    if hasattr(settings, "CACHED_BASIC_AUTH_MODEL_BACKEND")
    else False
)
# used for failed passwords, to check for reuse
_static_salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
User = get_user_model()


@dataclass
class CachedUser:
    user: Optional[User]
    hashed_password: Optional[str]  # a hash of the correct password.  None if the user has not authed successfully yet
    failed_hashed_passwords: set[str]  # UNIQUE incorrect password hashes
    locked_until: Optional[datetime]  # if set, the account is locked until this time


_user_cache: dict[str, CachedUser] = {}  # maps usernames to cached users


def _hash_password(password, use_static_hash: bool = False):
    """Hash a password for storing."""
    salt = _static_salt if use_static_hash else hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    encoded_password = (password or "").encode("utf-8")  # protect against password = None
    pwdhash = hashlib.pbkdf2_hmac("sha512", encoded_password, salt, HASH_ITERATIONS)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode("ascii")


def _verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    encoded_provided_password = (provided_password or "").encode("utf-8")  # protect against provided_password = None
    pwdhash = hashlib.pbkdf2_hmac("sha512", encoded_provided_password, salt.encode("ascii"), HASH_ITERATIONS)
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    return pwdhash == stored_password


def _record_successful_auth(user: User, hashed_password: str):
    """Perform required actions after successfully authenticating through Django"""
    # reset any previous cached data after a successful auth
    _user_cache[user.username] = CachedUser(user, hashed_password, failed_hashed_passwords=set(), locked_until=None)
    statsd.increment("auth.basic.success")


def _record_failed_auth(username: str, hashed_password: str):
    _logger.warning("Invalid login attempt", extra={"username": username})
    statsd.increment("auth.basic.failure")

    # if this is a new username, create a new empty cached record
    cached_user = _user_cache.get(username)
    if not cached_user:
        cached_user = CachedUser(
            user=User.objects.filter(username=username).first(),
            hashed_password=None,
            failed_hashed_passwords=set(),
            locked_until=None,
        )
        _user_cache[username] = cached_user
    # if the user is known, but locked, no need to do anything else
    elif cached_user.locked_until:
        return

    # record the password hash in a set, so we only see unique hashes
    cached_user.failed_hashed_passwords.add(hashed_password)

    # if there were too many unique hashes, then lock the user account temporarily to deter brute-force attacks
    if len(cached_user.failed_hashed_passwords) >= MAX_FAILED_ATTEMPTS:
        cached_user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_DURATION_MINUTES)
        _logger.error("User has been locked due to invalid password attempts", extra={"username": username})
        statsd.increment("auth.basic.lockout")

        # lock the user in the DB, if they have the attribute
        if cached_user.user and hasattr(cached_user.user, "locked_until"):
            cached_user.user.locked_until = make_aware(cached_user.locked_until)
            cached_user.user.save(update_fields=["locked_until"])

        # clear out the cached user's data, so future attempts will need to fully authenticate
        cached_user.user = None
        cached_user.hashed_password = None


class CachedBasicAuthModelBackend(ModelBackend):
    """
    A wrapper around the standard Django BASIC auth backend, supporting credential/user caching and new user fields.

    NOTE: This class is based off of the threat model of an internal service.  It has not been assessed for a public-
    facing service, especially one with non-blink user accounts.  Any such service should not be using basic auth
    though.

    When a user successfully authenticates, their hashed credentials and user object are cached in memory.  The
    credentials are hashed fewer times than the version stored in the database, so comparing incoming credentials to
    them is much faster, and doesn't require any database call.  Because the cached credentials are never written to
    disk, they don't need the same level of hashing, and they would still take years to crack if an attacker was ever
    to get them from memory.

    To protect against brute-force attempts at guessing a password, a user will be temporarily locked after too many
    failed authentication attempts with unique passwords.  This means that an invalid config that continuously tries the
    same wrong password won't lock the account, but cycling through different passwords will.  As this list is stored in
    memory, instead of a central location, an attacker would technically have more attempts when spread across multiple
    processes, but this amount would still be minuscule, and not alter their effectiveness.

    This also supports blocking users who are set to be locked "after" a certain date/time.  This allows granting a user
    temporary access that will be automatically locked after a certain time.  So if you wanted to grant a user access
    for an hour, so they could perform a single action, you could set their locked_after attribute to be an hour in the
    future.
    """

    def authenticate(self, request, username=None, password=None, **kwargs) -> Optional[User]:
        """Check a username/password against the user table, and return a User object if properly authenticated"""
        # if this user is already cached, and the password matches, return the cached user
        cached_user = _user_cache.get(username)
        if cached_user and cached_user.hashed_password and _verify_password(cached_user.hashed_password, password):
            # if the password matches what is cached, return the user.  if not, fall through and try to auth normally

            # refresh the user object if we don't want to return the cached version
            if not _return_cached_user:
                cached_user.user = User.objects.get(id=cached_user.user.id)

            return cached_user.user

        # try to authenticate through checking against users in the DB
        user = super().authenticate(request, username, password, **kwargs)

        # cache details about the authentication attempt, whether it was successful or not
        if user:
            _record_successful_auth(user, _hash_password(password))
        else:
            _record_failed_auth(username, _hash_password(password, use_static_hash=True))

        return user  # user is None if they were not authenticated

    def user_can_authenticate(self, user) -> bool:
        """
        A companion to authentication(), this checks if the user record is even allowed to authenticate

        It checks the is_active attribute, and the locked_after and locked_until attributes if they exist.
        """
        # if the base method fails (just checks is_active), then the user cannot authenticate
        if not super().user_can_authenticate(user):
            return False

        # if the user is locked, check if the lock has expired
        locked_until = getattr(user, "locked_until", None)
        if locked_until:
            # if still locked, the user cannot authenticate
            if make_aware(datetime.utcnow()) < locked_until:
                return False

            # if the lock has expired, then clear it out
            user.locked_until = None
            user.user.save(update_fields=["locked_until"])

        # if locked_after is set, and we are passed it, then user cannot authenticate
        locked_after = getattr(user, "locked_after", None)
        if locked_after and make_aware(datetime.utcnow()) > locked_after:
            return False

        return True
