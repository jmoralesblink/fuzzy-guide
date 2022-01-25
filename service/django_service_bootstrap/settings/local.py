from deepmerge import always_merger

from common_lib.service_enums import DeploymentEnvironments
from .base import *

DEBUG = True

ENVIRONMENT = os.environ.get("ENVIRONMENT", DeploymentEnvironments.local.value)

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
            "CONN_MAX_AGE": 600,
        }
    },
)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://172.28.1.4:6677/",
        "TIMEOUT": 60,  # 1min
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", "PASSWORD": "password"},
    }
}

# Blink middleware settings
HTTP_MAX_LOG_PAYLOAD = 200  # large request/response bodies make logging harder to read in the terminal
HTTP_LOG_HEADERS = False

LOGGING = always_merger.merge(
    LOGGING,
    {
        "handlers": {
            "console_error": {
                "formatter": "standard",  # makes stack traces easier to read
            },
        },
    },
)

QUEUES_CONFIG = always_merger.merge(
    QUEUES_CONFIG,
    {
        "aws_endpoint_url": "http://localhost:4566",  # Localstack endpoint
        "create_topic": True,
        "topics": {
            "django_service_bootstrap_general_queue": {
                "name": "django-service-bootstrap-general-local",
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

# read in any personal settings, as the highest priority (must be at the end of the file)
if os.path.exists("django_service_bootstrap/settings/personal.py"):
    from .personal import *
