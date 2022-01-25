import decimal

import respx
from django.conf import settings
from faker import Faker
from httpx import Response

from core.clients.mocks.client_mock_constants import DEFAULT_FOO_ID

# Retrieves the base url from settings file that we are going to mock
SETTINGS_CONFIG = settings.HTTP_CLIENTS["endpoints"]["foo"]
BASE_URL = SETTINGS_CONFIG["root_url"]

fake = Faker()


def get_foo_data(id: str = None, name: str = None, price: decimal = None) -> dict:
    """Creates a foo data dictionary of what the mocked foo service will return to us"""
    return {
        "id": id or DEFAULT_FOO_ID,
        "name": name or fake.pystr(),
        "price": price or str(fake.pydecimal(left_digits=2, right_digits=3, positive=True)),
    }


def get_foo_side_effect(request):
    id = request.url.path.rstrip("/").split("/")[-1]
    return Response(200, json=get_foo_data(id=id))


# Initializes a mocked router for the foo client
# Side effects are used as callbacks in this case to trigger a mocked response
foo_router = respx.Router(base_url=BASE_URL, assert_all_called=False)

get_foo_route = foo_router.get(path__regex="\\w+", name="get_foo")
get_foo_route.side_effect = get_foo_side_effect
