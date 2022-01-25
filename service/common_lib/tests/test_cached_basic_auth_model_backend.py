import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import RequestFactory

import common_lib.cached_basic_auth_model_backend as backend_mod

DEFAULT_USERNAME = "bilbo.baggins"
DEFAULT_PASSWORD = "password"
User = get_user_model()


class CachedBasicAuthModelBackendTest(TestCase):
    @pytest.fixture(scope="class", autouse=True)
    def create_user(self):
        User.objects.create_user(
            username=DEFAULT_USERNAME, email=f"{DEFAULT_USERNAME}@blinkhealth.com", password=DEFAULT_PASSWORD
        )

    def setUp(self):
        self.backend = backend_mod.CachedBasicAuthModelBackend()
        self.request = RequestFactory().get("")

    def test_successful_auth(self):
        result = self.backend.authenticate(self.request, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)

        self.assertEqual(result.username, DEFAULT_USERNAME)

    def test_unknown_username(self):
        result = self.backend.authenticate(self.request, username="not_a_valid_user", password="bad_password")

        self.assertIsNone(result)

    def test_none_username(self):
        result = self.backend.authenticate(self.request, username=None, password="bad_password")

        self.assertIsNone(result)

    def test_invalid_password(self):
        result = self.backend.authenticate(self.request, username=DEFAULT_USERNAME, password="bad_password")

        self.assertIsNone(result)

    def test_none_password(self):
        result = self.backend.authenticate(self.request, username=DEFAULT_USERNAME, password=None)

        self.assertIsNone(result)

    def test_lockout_blocks_login(self):
        # lockout the user
        backend_mod.MAX_FAILED_ATTEMPTS = 1
        self.backend.authenticate(self.request, username=DEFAULT_USERNAME, password="bad_password")

        # login correctly, which should still not auth, since the user is locked
        result = self.backend.authenticate(self.request, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)

        self.assertIsNone(result)
