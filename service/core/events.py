import logging
from enum import Enum

from common_lib.enum_mixin import EnumMixin
from common_lib.event import Event


class EventNames(EnumMixin, Enum):
    widget_created = "widget.create.success"
    widget_create_failed = "widget.create.failure"


class WidgetCreatedEvent(Event):
    event_name = EventNames.widget_created.value
    event_fields = ["public_id", "status?"]
    message = "Widget creation succeeded"
    log_level = logging.INFO
    emit_metric = True
    metric_tags = ["public_id", "status?"]


class WidgetCreateFailedEvent(Event):
    event_name = EventNames.widget_create_failed.value
    event_fields = ["public_id", "status?"]
    message = "Widget creation failed"
    log_level = logging.ERROR
    emit_metric = True
    metric_tags = ["public_id", "status?"]
