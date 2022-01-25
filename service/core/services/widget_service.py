import logging

from core.events import WidgetCreatedEvent
from core.models.widget import Widget
from core.services.event_service import record_event

_logger = logging.getLogger(__name__)


def create_widget(name: str):
    widget = Widget.objects.create(name=name)
    record_event(WidgetCreatedEvent(name=widget.name))
    return widget
