from django.apps import AppConfig
from django.conf import settings


class MessageConsumerConfig(AppConfig):
    name = "message_consumer"

    def ready(self):
        # importing consumer here so that we only load it when ready. Otherwise we will have issues when importing
        # methods from different apps when they are not yet loaded
        from message_consumer.consumer import start_consumer

        if settings.IS_API_NODE:
            start_consumer()
