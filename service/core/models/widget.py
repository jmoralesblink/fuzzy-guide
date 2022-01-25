import logging
import uuid

from django.db import models

from common_lib.base_model import BaseModel

_logger = logging.getLogger(__name__)


class Widget(BaseModel):
    # public GUID sent to other other services as our identifier
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=32)
