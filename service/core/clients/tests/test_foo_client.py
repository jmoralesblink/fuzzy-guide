import json
import pytest
from django.conf import settings
from common_lib.errors import BlinkError
from common_lib.mock_http_response import MockHttpResponse
from core.clients.foo_client import get_foo, get_foo_async
from core.clients.mocks.foo_client_mocks import get_foo_data, get_foo_route
from core.dtos import Foo

# Retrieves the base url from settings file
SETTINGS_CONFIG = settings.HTTP_CLIENTS["endpoints"]["foo"]
BASE_URL = SETTINGS_CONFIG["root_url"]


def test_retrieve_foo_success():
    foo_data = get_foo_data()
    foo_json = json.dumps(foo_data)
    with MockHttpResponse(get_foo_route, 200, foo_data, assert_called=True):
        response = get_foo(foo_data["id"])
        assert response.to_json() == Foo.from_json(foo_json).validate().to_json()


def test_retrieve_foo_failed():
    foo_data = get_foo_data()
    with pytest.raises(BlinkError):
        with MockHttpResponse(get_foo_route, 404, {}, assert_called=True):
            response = get_foo(foo_data["id"])


@pytest.mark.asyncio
async def test_retrieve_foo_success_async():
    foo_data = get_foo_data()
    foo_json = json.dumps(foo_data)
    async with MockHttpResponse(get_foo_route, 200, foo_data, assert_called=True):
        response = await get_foo_async(foo_data["id"])
        assert response.to_json() == Foo.from_json(foo_json).validate().to_json()


@pytest.mark.asyncio
async def test_retrieve_foo_failed_async():
    foo_data = get_foo_data()
    with pytest.raises(BlinkError):
        with MockHttpResponse(get_foo_route, 404, {}, assert_called=True):
            response = await get_foo_async(foo_data["id"])
