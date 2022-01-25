import logging
from threading import Thread

from blink_messaging import consumer
from django.conf import settings

from core.constants import INTERNAL_QUEUE_TOPIC_NAME

_logger = logging.getLogger(__name__)
_topics = [settings.TOPIC_CONFIG[INTERNAL_QUEUE_TOPIC_NAME]]
_topic_names = ", ".join(t.name for t in _topics)
_consumer_thread: Thread = None

_handler_map = {
    # Here we will map the message to the handler
    # Ex: PendingFooSubmissionDTO: handle_foo_submission_request,
}


def start_consumer():
    """Start the blink-messaging consumer for all topics."""
    global _consumer_thread
    if _consumer_thread and _consumer_thread.is_alive():
        _logger.warning("Trying to start the consumer while it's already running", extra={"topics": _topic_names})
        return

    try:
        _consumer_thread = consumer.startup(
            topics=_topics,
            message_handler=handle_message,
            error_handler=error_handler,
            use_background_thread=True,
        )
        _logger.info("Started consumer", extra={"topics": _topic_names})
    except Exception as e:
        _logger.exception("Failed to start consumer", extra={"topics": _topic_names, "message": e})


def handle_message(message, confirm_handler):
    # check if message handler exists, if not exit early
    message_type = type(message)
    _logger.info(
        f"Starting to handle message of type {message.Meta.full_name}:{message.Meta.version}.",
        extra={"data": message.to_json()},
    )
    message_handler = _handler_map.get(message_type, None)

    if message_handler is None:
        _logger.error(f"No handler is registered for message type {message_type}. Discarding message.")
        confirm_handler()
        return

    # message validation
    try:
        message.validate()
    except Exception as e:
        _logger.exception(
            "BlinkMessage failed validation on consumption.",
            extra={"message": e, "data": message.to_json()},
        )
        return

    # call handler method and process message
    try:
        message_handler(message)
    except Exception as e:
        _logger.exception(
            f"Failed to handle message: {message.Meta.full_name}:{message.Meta.version}",
            extra={"data": message.to_json()},
        )

        # returning without confirming the message will cause it to go to the DLQ
        return

    # if all went well, confirm that message was handled
    confirm_handler()


def error_handler(error):
    _logger.error(f"Unhandled error when processing a topic message", exc_info=error)


def process_topics():
    """
    Run the blink-message consumer against all topics once, and return the number of messages processed.

    This will also cause the consumer to run on the main thread, instead of a background one.  Useful for unit tests.
    :return: Returns a tuple (success_count, failure_count) of messages processed
    """
    return consumer.process_topics(topics=_topics, message_handler=handle_message, error_handler=error_handler)
