from unittest import TestCase
from unittest.mock import Mock

from django.http import Http404
from django.template import Context

from common_lib.django.drf.error_handling import global_drf_exception_handler
from common_lib.error_reason_types import ErrorReasonTypes
from common_lib.errors import BlinkError


class TestCustomDrfExceptionHandler(TestCase):
    def setUp(self):
        self.mock_context = Mock(Context)

    def test_default_error(self):
        response = global_drf_exception_handler(Exception("msg"), self.mock_context)
        self.assertEqual(500, response.status_code)
        self.assertEqual("Unhandled internal error.  See logs for details.", response.data["error"])

    def test_default_rxerror(self):
        response = global_drf_exception_handler(BlinkError(), self.mock_context)
        self.assertEqual(500, response.status_code)
        self.assertEqual("An internal server error occurred", response.data["error"])

    def test_custom_error_reason(self):
        response = global_drf_exception_handler(
            BlinkError("msg", reason_type=ErrorReasonTypes.conflict.value), self.mock_context
        )
        self.assertEqual(409, response.status_code)
        self.assertEqual("msg", response.data["error"])

    def test_drf_error(self):
        response = global_drf_exception_handler(Http404(), self.mock_context)
        self.assertEqual(404, response.status_code)
        self.assertNotIn("error", response.data)
