import json
from typing import Tuple, List

from blink_messaging import consumer, BlinkTopic
from blink_messaging.publisher import publish
from blink_messaging.serialization import BlinkMessage
from django.conf import settings

from common_lib.cli import prompt


def _load_and_print_topic_messages(topic: BlinkTopic) -> List[Tuple[BlinkMessage, callable]]:
    # define a router that stores each message as a tuple of (message, confirm_handler())
    messages = []

    def _router(message, confirm_handler):
        messages.append((message, confirm_handler))

    # read messages from the topic
    success_count, failure_count = consumer.process_topics(topics=[topic], message_handler=_router)

    # display all messages to the user
    prompt.print()
    for i, message_tuple in enumerate(messages):
        message, confirm_handler = message_tuple
        prompt.print_key_value("Message", f"{i + 1}) {message.Meta.full_name}:{message.Meta.version}")
        prompt.print(json.dumps(json.loads(message._json_data), indent=2))

    if len(messages) == 0:
        prompt.print_warning("No messages found.")

    return messages


def manage_dlq():
    # select a DLQ to manage
    dlq_topic_names = [key for key in settings.TOPIC_CONFIG.keys() if "_dlq" in key]
    topic_name = prompt.get_option("Select a topic", dlq_topic_names)
    topic = settings.TOPIC_CONFIG[topic_name]

    # display available messages from the topic
    messages = _load_and_print_topic_messages(topic)

    # prompt user for possible actions
    action = ""
    while action != "Done" and messages:
        num_messages = len(messages)
        action = prompt.get_option("Action", ["Re-Send", "Delete", "Purge Queue", "Refresh", "Done"])

        # process queue-level actions
        if action == "Done":
            continue
        elif action == "Purge Queue":
            # inform the user what actions will be performed
            if not prompt.get_bool(
                "This will remove ALL messages from this DLQ, including ones that you may not have seen.  Continue?"
            ):
                prompt.print_error("Cancelling action")
                continue
            topic.purge()
            continue
        elif action == "Refresh":
            messages = _load_and_print_topic_messages(topic)
            continue

        # process message-level actions
        message_index = prompt.get_int("Message index") - 1
        if message_index >= num_messages or message_index < 0:
            prompt.print_error(f"Message index out of bounds: {message_index}")
            continue
        message, confirm_handler = messages[message_index]
        if action == "Re-Send":
            source_topic = settings.TOPIC_CONFIG[topic_name.replace("_dlq", "")]
            publish(source_topic, message)
            confirm_handler()
        elif action == "Delete":
            confirm_handler()
