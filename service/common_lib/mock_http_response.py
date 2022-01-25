from typing import Callable, Union

import respx
from httpx import Response


class MockHttpResponse:
    """
    A context manager for updating the response of a client mock transport

    You specify a Respx route, as well as settings on how you want it to respond during any code within its context.
    This gives you full control over what is returned, as well as side-effects, and asserting if it was or was not
    called.

    The response data can either be a raw string, or a json dict.

    Ex:
    with MockHttpResponse(get_prescription_fill_route, 500, {}, assert_called=False):
        foo = submit_foo(submit_foo_request, user)
    """

    def __init__(
        self,
        route: respx.router.Route,
        resp_code: int = 200,
        resp_data: Union[dict, str] = "",
        side_effect: Callable = None,
        assert_called: bool = False,
        assert_not_called: bool = False,
    ):
        self._route = route
        self._resp_code = resp_code
        self._resp_data = resp_data
        self._side_effect = side_effect
        self._assert_called = assert_called
        self._assert_not_called = assert_not_called

    def __enter__(self):
        # reset call history
        self._route.reset()

        # store original return_value and side effect
        self._orig_return_value = self._route.return_value
        self._orig_side_effect = self._route.side_effect

        self._route.return_value = (
            Response(self._resp_code, content=self._resp_data)
            if isinstance(self._resp_data, str)
            else Response(self._resp_code, json=self._resp_data)
        )
        self._route.side_effect = self._side_effect

    async def __aenter__(self):
        self.__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # When we're done using this context, revert back to original values
        self._route.return_value = self._orig_return_value
        self._route.side_effect = self._orig_side_effect

        # optinally assert the route was called
        if self._assert_called:
            try:
                self._route.calls.assert_called()
            except AttributeError:
                # a confusing AttributeError is thrown when not called, so make a clearer error
                raise AssertionError(f"Expected route not called: {self._route.name}")

        # optinally assert the route was NOT called
        if self._assert_not_called:
            try:
                self._route.calls.assert_not_called()
            except AttributeError:
                # a confusing AttributeError is thrown when called, so make a clearer error
                raise AssertionError(f"Un-expected route called: {self._route.name}")

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        self.__exit__(exc_type, exc_value, exc_traceback)
