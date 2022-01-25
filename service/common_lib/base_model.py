from django.db import models
from django.utils import timezone
from safedelete.managers import (
    SafeDeleteManager,
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
)
from safedelete.models import SafeDeleteModel
from safedelete.queryset import SafeDeleteQueryset
from safedelete.config import SOFT_DELETE_CASCADE


class BlinkQuerySet(SafeDeleteQueryset):
    """A wrapper around the standard queryset, to allow custom processing"""

    def update(self, **kwargs):
        """Perform additional processing on every queryset update"""
        # ensure modified_date is always updated along with other fields
        if "modified_date" not in kwargs and hasattr(self.model, "modified_date"):
            kwargs["modified_date"] = timezone.now()

        super().update(**kwargs)


class BlinkManager(SafeDeleteManager):
    """A wrapper around the standard manager, to allow custom processing"""

    # Return our custom queryset class, instead of the standard one, when using Model.objects.some_method()
    _queryset_class = BlinkQuerySet


class BlinkAllManager(SafeDeleteAllManager):
    """A wrapper around the standard manager, to allow custom processing"""

    # Return our custom queryset class, instead of the standard one, when using Model.objects.some_method()
    _queryset_class = BlinkQuerySet


class BlinkDeleteManager(SafeDeleteDeletedManager):
    """A wrapper around the standard manager, to allow custom processing"""

    # Return our custom queryset class, instead of the standard one, when using Model.objects.some_method()
    _queryset_class = BlinkQuerySet


class BlinkSafeDeleteModel(SafeDeleteModel):
    """A wrapper around the SafeDelete base model, to allow custom processing"""

    objects = BlinkManager()
    all_objects = BlinkAllManager()
    deleted_objects = BlinkDeleteManager()

    class Meta:
        abstract = True


class BaseModel(BlinkSafeDeleteModel):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    deleted = models.DateTimeField(editable=False, null=True, db_index=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        abstract = True

    def save(self, keep_deleted=False, **kwargs):
        """Perform additional processing on every model save"""
        # ensure that modified_date is always included as a save field
        upd_fields = kwargs.get("update_fields")
        if upd_fields and "modified_date" not in upd_fields and hasattr(self, "modified_date"):
            upd_fields.append("modified_date")

        super().save(keep_deleted=keep_deleted, **kwargs)
