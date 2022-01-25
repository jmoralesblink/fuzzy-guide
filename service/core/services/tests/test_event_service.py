import logging
from unittest import mock

import pytest

from common_lib.event import Event
from core.services import event_service


class LogOnlyEvent(Event):
    event_name = "test.event"
    event_fields = ["test_tag"]
    message = "Test event message"
    log_level = logging.INFO


# using a test that doesn't inherit from UnitTest allows me to use pytest fixture arguments, but requires marking
# the test with django_db, and using normal assert statements
@pytest.mark.django_db
class TestRecordEvent:
    # @pytest.fixture(scope="function", autouse=True)
    # def mock_on_commit(self):
    #     with mock.patch("django.db.transaction.on_commit", lambda t: t()):
    #         yield

    @pytest.fixture(scope="function", autouse=False)
    def mock_statsd(self):
        with mock.patch("core.services.event_service.statsd.increment") as mock_statsd:
            yield mock_statsd

    def test_log_only(self, caplog, mock_statsd):
        # arrange
        event = LogOnlyEvent(test_tag="Log")

        # act
        event_service.record_event(event)

        # assert
        mock_statsd.assert_not_called()
        assert "Test event message" in caplog.text

    def test_metric_only(self, caplog, mock_statsd):
        # arrange
        event = LogOnlyEvent(test_tag="Metric")
        event.log_level = logging.NOTSET
        event.emit_metric = True
        event.metric_tags = ["test_tag"]

        # act
        event_service.record_event(event)

        # assert
        mock_statsd.assert_called_once()
        assert len(caplog.records) == 0

    def test_log_and_metric(self, caplog, mock_statsd):
        # arrange
        event = LogOnlyEvent(test_tag="Log")
        event.emit_metric = True
        event.metric_tags = ["test_tag"]

        # act
        event_service.record_event(event)

        # assert
        mock_statsd.assert_called_once()
        assert "Test event message" in caplog.text
