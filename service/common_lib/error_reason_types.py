from enum import unique, Enum

from common_lib.enum_mixin import EnumMixin
from rest_framework.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
)

"""
This file stores the error reason types that BlinkError uses. 
The error reason types can be switched out with other reason types if needed or switched out for another Enum class
"""


@unique
class ErrorReasonTypes(EnumMixin, Enum):
    """
    These are broad  error reason "types" and shouldn't include specific error "reasons".
    Should be broad enough to be mappable to an HTTP status
    """

    not_found = "not_found"
    internal_error = "internal_error"
    bad_request = "bad_request"
    forbidden = "forbidden"
    unauthorized = "unauthorized"
    conflict = "Conflict"
    validation_error = "Validation Error"


REASON_TYPE_TO_HTTP_STATUS = {
    ErrorReasonTypes.not_found.value: HTTP_404_NOT_FOUND,
    ErrorReasonTypes.internal_error.value: HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorReasonTypes.bad_request.value: HTTP_400_BAD_REQUEST,
    ErrorReasonTypes.forbidden.value: HTTP_403_FORBIDDEN,
    ErrorReasonTypes.unauthorized.value: HTTP_401_UNAUTHORIZED,
    ErrorReasonTypes.conflict.value: HTTP_409_CONFLICT,
    ErrorReasonTypes.validation_error.value: HTTP_400_BAD_REQUEST,
}
