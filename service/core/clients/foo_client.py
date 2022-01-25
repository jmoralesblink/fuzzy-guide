from common_lib.blink_requests_async import get_client, get_response
from common_lib.errors import BlinkError
from core.dtos import Foo


def _get_client():
    return get_client("foo", is_async=False)


def _get_async_client():
    return get_client("foo", is_async=True)


def get_foo(foo_id: str) -> Foo:
    try:
        response = _get_client().get(f"/{foo_id}/")
        return Foo.from_json(get_response(response)).validate()
    except Exception as ex:
        raise BlinkError(f"Failed to get foo data. {ex}")


async def get_foo_async(foo_id: str) -> Foo:
    try:
        response = await _get_async_client().get(f"/{foo_id}/")
        return Foo.from_json(get_response(response)).validate()
    except Exception as ex:
        raise BlinkError(f"Failed to get foo data. {ex}")
