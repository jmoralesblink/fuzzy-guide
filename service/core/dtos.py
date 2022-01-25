"""
Internal DTO classes, used for moving complex state throughout the code

These include all DTOs that are not part of a public contract of this service (HTTP or async messages), and includes
DTOs used to get data from other services.

Inherit from BlinkSubMessage, so that we don't need to define meta-data, that is only needed for externally published
messages.
"""

from blink_messaging.serialization import fields, BlinkSubMessage


class Foo(BlinkSubMessage):
    id = fields.String(max_len=60)
    name = fields.String(max_len=50)
    price = fields.Decimal()
