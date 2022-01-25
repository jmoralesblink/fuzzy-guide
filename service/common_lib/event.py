import logging

from dataclasses import dataclass
from typing import List

_logger = logging.getLogger(__name__)


@dataclass
class EventField:
    """Used by EventMeta to store information about event fields"""

    name: str
    is_required: bool  # True if there is no default value, so it must be passed in
    allow_none: bool  # True if None is allowed.  A field might be required, but still allow None, or vice-versa
    default_value: object
    is_kwargs: bool  # True if the field starts with '**', and allows any field to be added to the event


class Event:
    """
    Base event class to automatically parse, validate and store args on construction.

    All event classes should be defined as shown below.

    class MyCustomEvent(Event):
        event_name = "patient.insurance.set_primary"
        event_fields = ["patient_id", "order_status", "insurance_id", "created_by_id?", "order_id=None", "**kwargs"]
        message = "patient insurance {patient_id} set as primary"
        log_level = logging.INFO
        emit_metric = True
        metric_tags = ["order_status", "created_by_id"]

        def init(self):
            print("This is an optional custom initialization function")

    # Event Attributes
    All attributes after event_name and event_fields are optional, and the init() function is optional as well.

    * event_name: The name of the event, used as the log message and metric name
    * event_fields: A list of parameters the event will expect in its constructor, and be stored in `tags`.
        * When a field name ends with a question mark, it is allowed to be set to null, but is still required to be
          passed in.  If it does NOT have a question mark, then an error will be thrown if None is passed in.
        * If a default value of None is given, then the field will also allow None to be passed in, or to not be passed
          in at all.
        * If the last field starts with '**', then all non-defined fields will be allowed.
    * message: If set, will be included in the log message.  It will processed with the format() function, passing in
        all values passed in from `event_fields`.
    * log_level: Determines the level to log the event at.  If it is set to logging.NOTSET, then the event will not be
        logged.  This is useful if you want an event to be emitted as a metric only.
        * Default: logging.INFO
    * emit_metric: If `True`, a metric will be emitted for this event.
        * Default: `False`
    * metric_tags: If set, the listed event_fields will be included as tags in the emitted metric.
        * Default: empty list
    * metric_increment_field: If `set, the event field referenced will determine how much to increment the metric.  If
        not set, the field would be incremented by 1.
        * Default: None
    """

    # required to be set by sub-classes
    event_name: str = None
    event_fields: str = None
    message = None
    # optional for sub-classes to set
    log_level: int = logging.INFO
    emit_metric: bool = False
    metric_tags: List[str] = []
    metric_increment_field: str = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.event_name!r}, {self.tags!r})"

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.tags == other.tags and self.event_name == other.event_name
        return NotImplemented

    def __ne__(self, obj):
        return not self == obj

    @staticmethod
    def _parse_field(field: str):
        """
        Takes a field definition as a string, and parses it into an EventField object

        A field definition might look like "field_name", "field_name?" or "field_name=None" (None could be any default)
        """
        is_required = True
        default_value = None
        allow_none = False

        # check for a default value, and parse it
        if "=" in field:
            is_required = False
            field_parts = field.split("=")
            field = field_parts[0]
            default_value = field_parts[1]
            if default_value == "None":
                default_value = None
                allow_none = True
            elif default_value == "True":
                default_value = True
            elif default_value == "False":
                default_value = False
            elif "'" in default_value:
                default_value = default_value.replace("'", "")
            elif "." in default_value:
                default_value = float(default_value)
            else:
                default_value = int(default_value)

        # check if the field allows None
        if field.endswith("?"):
            allow_none = True
            field = field[:-1]

        # check if the field allows kwargs
        is_kwargs = field.startswith("**")
        if is_kwargs:
            is_required = False

        return EventField(field, is_required, allow_none, default_value, is_kwargs)

    def _parse_field_definitions(self):
        """
        Parse all field info, to be used for parameter validation during event construction.

        :return: a list of EventField definitions
        """
        # ensure required fields exist
        if not self.event_name:
            raise ValueError("Class definition does not define 'event_name'")
        if not self.event_fields:
            raise ValueError("Class definition does not define 'event_fields'")

        # parse all fields
        fields = []
        default_found = False  # once True, all remaining fields must have a default value
        for field_def in self.event_fields:
            field = self._parse_field(field_def)

            # track once a default field has been found
            if not field.is_required:
                default_found = True

            # ensure a field with no default didn't come after a field that had one
            if field.is_required and default_found:
                raise ValueError(f"Required field {field_def} can't be defined after an optional field")

            if field.is_kwargs and field_def != self.event_fields[-1]:
                raise ValueError(f"**kwargs fields can only be added as the last parameter.")

            # store the field info
            fields.append(field)

        # update body, and create class
        return fields

    def __init__(self, *args, **kwargs):
        """Validate all constructor parameters, and store them in self.tags"""
        if not hasattr(self, "_fields"):
            self.__class__._fields = self._parse_field_definitions()

        tags = dict()
        fields = self._fields
        allow_any_parameter = fields[-1].is_kwargs

        # read in all arguments
        for i, arg in enumerate(args):
            tags[fields[i].name] = arg
        for key, value in kwargs.items():
            if not any(f.name == key for f in fields) and not allow_any_parameter:
                raise ValueError(f"Field {key} was not defined for {self.__class__.__name__}")
            tags[key] = value

        # validate fields, and set default values
        for field in fields:
            if field.is_kwargs:
                continue
            if field.name not in tags:
                if field.is_required:
                    raise ValueError(f"Field {field.name} was not set for {self.__class__.__name__}")
                else:
                    tags[field.name] = field.default_value
            if not field.allow_none and tags[field.name] is None:
                raise ValueError(f"Required field {field.name} is None for {self.__class__.__name__}")

        # set message, if defined
        if self.message:
            self.message = self.message.format(**tags)

        # set tags
        self.tags = tags

        # run custom initialization, if defined
        if hasattr(self, "init"):
            self.init(self.tags)
