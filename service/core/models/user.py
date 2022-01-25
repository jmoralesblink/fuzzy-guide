from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Override the base user model, allowing us to add additional attributes as needed.

    This requires AUTH_USER_MODEL to point to here in the settings, for Django to recognize it, and it needs to be set
    when first creating the database (so it exists in the 0001_initial.py migration).

    The lockout functionality provided by locked_after and locked_until are secondary to the main is_active attribute,
    so any non-active user is disabled, regardless of their locked status.
    """

    # lock the user account after a datetime.  this allows permanently locking an account immediately, or in the
    # future, which allows granting temporary access
    locked_after = models.DateTimeField(null=True, blank=True)
    # lock the user account until a datetime.  this allows temporarily locking an account, such as after too many
    # failed login attempts
    locked_until = models.DateTimeField(null=True, blank=True)

    # the tenant the user/service is associated with
    tenant_id = models.CharField(max_length=64, null=True)

    # The key to topic config against which the updates of async API calls are published.
    # if this value is null, async updates will not be published to the client.
    topic_name = models.CharField(max_length=64, null=True)
