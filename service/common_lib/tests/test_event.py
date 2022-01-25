from unittest import TestCase

from common_lib.event import Event


class TestEvent(TestCase):
    def test_event_name(self):
        class NameEvent(Event):
            event_name = "test_name"
            event_fields = ["param1"]

        event = NameEvent("val1")

        self.assertEqual(event.event_name, "test_name")

    def test_ordinal_parameters(self):
        class OrdinalEvent(Event):
            event_name = "name"
            event_fields = ["param1", "param2"]

        event = OrdinalEvent("val1", "val2")

        self.assertEqual(event.tags["param1"], "val1")
        self.assertEqual(event.tags["param2"], "val2")

    def test_kwarg_parameters(self):
        class KwargEvent(Event):
            event_name = "name"
            event_fields = ["param1", "param2"]

        event = KwargEvent(param1="val1", param2="val2")

        self.assertEqual(event.tags["param1"], "val1")
        self.assertEqual(event.tags["param2"], "val2")

    def test_default_values(self):
        class DefaultEvent(Event):
            event_name = "name"
            event_fields = ["param1", "param2=-1"]

        event = DefaultEvent("val1")
        self.assertEqual(event.tags["param1"], "val1")
        self.assertEqual(event.tags["param2"], -1)

        event = DefaultEvent("val1", 20)
        self.assertEqual(event.tags["param1"], "val1")
        self.assertEqual(event.tags["param2"], 20)

    def test_optional_values(self):
        class RequiredEvent(Event):
            event_name = "name"
            event_fields = ["param1?", "param2"]

        event = RequiredEvent(None, "val2")

        self.assertEqual(event.tags["param1"], None)
        self.assertEqual(event.tags["param2"], "val2")

    def test_param_validation(self):
        class ValidationEvent(Event):
            event_name = "name"
            event_fields = ["param1", "param2"]

        # required field not set
        with self.assertRaises(ValueError):
            event = ValidationEvent("val1")

        # non-nullable field set to None
        with self.assertRaises(ValueError):
            event = ValidationEvent("val1", None)

        # additional positional parameter
        with self.assertRaises(IndexError):
            event = ValidationEvent("val1", "val2", "val3")

        # un-known kwarg
        with self.assertRaises(ValueError):
            event = ValidationEvent("val1", param_unknown="val2")
