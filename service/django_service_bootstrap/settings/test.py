from deepmerge import always_merger

from common_lib.service_enums import DeploymentEnvironments
from .base import *

DEBUG = True

ENVIRONMENT = os.environ.get("ENVIRONMENT", DeploymentEnvironments.test.value)

# Use in-memory database for tests
DATABASES = always_merger.merge(
    DATABASES,
    {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "django_service_bootstrap_local",
            "USER": "django_service_bootstrap",
            "PASSWORD": "django_service_bootstrap",
            "HOST": "localhost",
            "PORT": 5544,
        }
    },
)

QUEUES_CONFIG = always_merger.merge(
    QUEUES_CONFIG,
    {
        "create_topic": True,
        "topics": {
            "django_service_bootstrap_general_queue": {
                "name": "django-service-bootstrap-general-test",
                "is_mocked": True,
            },
            "django_service_bootstrap_general_queue_dlq": {
                "name": "django-service-bootstrap-general-dlq-local",
                "is_mocked": True,
            },
        },
    },
)
TOPIC_CONFIG = BlinkTopic.load_from_config(QUEUES_CONFIG)

HTTP_CLIENTS = {
    "endpoints": {
        "foo": {
            "root_url": "http://test.foo.com/api/v1/foo",
            "auth": {"username": "django-service-bootstrap-test", "password": "django-service-bootstrap-test"},
            "mocked_transport": {"path": "core.clients.mocks.foo_client_mocks", "name": "foo_router"},
        },
    },
}
