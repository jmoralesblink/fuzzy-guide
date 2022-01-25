import factory
from faker import Faker

from core.constants import BLINK_TENANT_ID, INTERNAL_QUEUE_TOPIC_NAME
from core.models import User, Widget

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)  # handles duplicate key constraint issue caused by multiple instances

    username = fake.pystr(min_chars=5, max_chars=15)
    email = fake.email()
    password = fake.pystr(min_chars=5, max_chars=15)
    tenant_id = BLINK_TENANT_ID
    topic_name = INTERNAL_QUEUE_TOPIC_NAME


class WidgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Widget

    public_id = fake.uuid4()
    name = fake.pystr(max_chars=32)
