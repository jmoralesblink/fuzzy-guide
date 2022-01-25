from threading import current_thread
from django.db import models


class TenantAwareManager(models.Manager):
    def get_queryset(self):
        tenant_id = current_thread().tenant_id if hasattr(current_thread(), "tenant_id") else None
        return super().get_queryset().filter(tenant__id=tenant_id) if tenant_id else super().get_queryset()


class TenantAwareModelMixin(models.Model):
    """
    A mixin class for automatically adding tenant filtering to a model.

    In  order for this to work, it requires TenantIdMiddleware. Filtering only works within the context
    of a request and anything else not part of a request will not be filtered by the tenant.

    For accessing all objects without filtering, unscoped can be used.
    """

    tenant_id = models.CharField(max_length=32, null=True)

    objects = TenantAwareManager()
    unscoped = models.Manager()

    class Meta:
        abstract = True
