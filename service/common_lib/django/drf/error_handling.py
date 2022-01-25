import logging

from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler
from blink_messaging.exceptions import ValidationError

from common_lib.errors import BlinkError

_logger = logging.getLogger(__name__)
WARNING_ERROR_TYPES = [NotAuthenticated]


def global_drf_exception_handler(exc, context):
    """
    Custom error handler for Django Rest Framework, ensuring a standard format for all un-handled errors

    Handles any errors that are not caught during a request and ensures they are returned from the API with a standard
    format.  If the error is (or inherits from) BlinkError or ValidationError, then set the HTTP status code as well.
    :param exc: The un-handled exception
    :param context: Additional context about the request that the error came from
    :return: A formatted response with the error in a JSON object
    """
    if isinstance(exc, BlinkError):
        status_code = exc.http_status
        message = str(exc)
        meta_data = exc.meta_data
    elif isinstance(exc, ValidationError):  # blink-messaging validation error
        status_code = HTTP_400_BAD_REQUEST
        message = f"Error validating DTO data: {str(exc)}"
        meta_data = exc.source_data
    else:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        message = "Unhandled internal error.  See logs for details."
        meta_data = dict()

    # try to get additional meta-data for the exception that will be logged
    extra = {"status": status_code, "meta_data": meta_data}
    try:
        view_type = type(context["view"])
        extra["view_type"] = f"{view_type.__module__}.{view_type.__qualname__}"

        request = context["request"]
        extra["url"] = request.get_full_path()
        if "REMOTE_HOST" in request.META:
            extra["remote_host"] = request.META["REMOTE_HOST"]
    except Exception as ex:
        # swallow any errors here, so we don't break the error handler
        _logger.exception(f"Failure getting exception metadata", exc_info=ex)

    # log the error, but some error types are just warnings
    if any(isinstance(exc, et) for et in WARNING_ERROR_TYPES):
        _logger.warning(str(exc), exc_info=exc, extra=extra)
    else:
        _logger.error(str(exc), exc_info=exc, extra=extra)

    # try calling REST framework's default exception handler first, which handles its own error types
    response = exception_handler(exc, context)
    if response:
        return response

    # handle other exceptions, setting the response's status code if the exception provides it
    return Response({"error": message}, status_code)
