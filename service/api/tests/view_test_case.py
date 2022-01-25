from django.test import TestCase
from rest_framework.test import APIClient

from core.tests.test_scenarios import create_user


class ViewTestCase(TestCase):
    """A base test case class that creates a user and authenticated client"""

    def setUp(self):
        self.user = create_user()
        self.authenticated_client = self._authenticated_client(self.user)
        self.unauthenticated_client = self._unauthenticated_client()

    @staticmethod
    def _authenticated_client(authenticated_user):
        client = APIClient()
        client.force_authenticate(user=authenticated_user)
        return client

    @staticmethod
    def _unauthenticated_client():
        return APIClient()
