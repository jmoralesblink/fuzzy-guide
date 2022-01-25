import logging

from blink_logging_metrics.metrics import statsd
from django.db import transaction

from common_lib.event import Event

_logger = logging.getLogger(__name__)


def record_event(event: Event, on_commit=True):
    """
    Records details of an event object, either by logging, emitting a metric, or both.

    If logging within a transaction.atomic block, on_commit determines if it should wait for the transaction to commit
    successfully before recording the event.  For error events though, they will always be logged immediately, since
    the commit would not be completed.

    :param event: The event to record
    :param on_commit: Whether or not to send the tick after transaction is committed
    """
    # warnings and errors should always be logged
    if event.log_level >= logging.ERROR:
        on_commit = False

    if on_commit:
        transaction.on_commit(lambda: _record_event(event))
    else:
        _record_event(event)


def _record_event(event: Event):
    # log the event if there is a log level
    if event.log_level:
        log_message = f"{event.event_name}: {event.message}" if event.message else event.event_name
        _logger.log(event.log_level, log_message, extra=event.tags)

    # emit the metric, if requested
    if event.emit_metric:
        tags = [f"{tag}:{event.tags[tag]}" for tag in event.metric_tags] if event.metric_tags else None
        increment_by = event.tags[event.metric_increment_field] if event.metric_increment_field else 1
        statsd.increment(event.event_name, value=increment_by, tags=tags)
