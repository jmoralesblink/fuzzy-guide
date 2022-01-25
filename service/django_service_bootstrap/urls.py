import logging

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


_logger = logging.getLogger(__name__)
_schema_view = get_schema_view(
    openapi.Info(title="Django Service Bootstrap API", default_version="v1"),
)

admin.site.site_header = "Django Service Bootstrap Admin Panel"
admin.site.site_title = "Django Service Bootstrap Admin"
admin.site.index_title = admin.site.site_header


def healthcheck(request):
    """
    Basic healthcheck that ensures secrets are loaded

    This gets called 11 times at once, every 10 seconds, from the k8s ingress check, so make sure it is quick.
    """
    if not settings.ALL_VAULT_SECRETS_LOADED:
        return HttpResponse("Vault secrets not loaded", status=500)

    return HttpResponse("Health Check", status=200)


urlpatterns = [
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
    path("healthcheck/", healthcheck),
    path("swagger/", _schema_view.with_ui()),
]
# For serving static files when DEBUG=True
urlpatterns += staticfiles_urlpatterns()
