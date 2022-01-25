from blink_messaging import BlinkTopic
from deepmerge import always_merger

from common_lib.service_enums import DeploymentEnvironments
from . import secrets_manager
from .base import *

DB_SECRETS = secrets_manager.get_database_secrets(require_data=True)
REDIS_SECRETS = secrets_manager.get_redis_secrets(require_data=True)
ALL_VAULT_SECRETS_LOADED = True

ENVIRONMENT = os.environ.get("ENVIRONMENT", DeploymentEnvironments.prod.value)

MIDDLEWARE = MIDDLEWARE + [
    "whitenoise.middleware.WhiteNoiseMiddleware"  # static files for the admin UI.  only needed in prod
]

DATABASES = always_merger.merge(
    DATABASES,
    {
        "default": {
            "NAME": DB_SECRETS["db"],
            "USER": DB_SECRETS["user"],
            "PASSWORD": DB_SECRETS["password"],
            "HOST": DB_SECRETS["host"],
            "PORT": DB_SECRETS["port"],
        }
    },
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

METRICS["statsd"]["hostname"] = "dogstatsd.datadog.svc.cluster.local"

QUEUES_CONFIG = always_merger.merge(
    QUEUES_CONFIG,
    {
        "topics": {
            "django_service_bootstrap_general_queue": {"name": "django-service-bootstrap-general-prod"},
            "django_service_bootstrap_general_queue_dlq": {"name": "django-service-bootstrap-general-dlq-prod"},
        },
    },
)
TOPIC_CONFIG = BlinkTopic.load_from_config(QUEUES_CONFIG)
