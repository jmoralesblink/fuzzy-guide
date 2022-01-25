from common_lib.error_reason_types import ErrorReasonTypes, REASON_TYPE_TO_HTTP_STATUS


class BlinkError(Exception):
    """
    Base error class that allows you to use high level reasons for an error and/or retrieve HTTP status code if error
    is associated with one. To add a new type of error add it to CommonErrors and to add an HTTP status associated
    with that error add it to REASON_TYPE_TO_HTTP_STATUS.
    """

    default_message = "An internal server error occurred"
    default_reason_type = ErrorReasonTypes.internal_error.value
    default_meta_data = dict()

    def __init__(self, message=None, reason_type=None, meta_data=None):
        self.message = message or self.default_message
        self.reason_type = reason_type or self.default_reason_type
        self.meta_data = meta_data or self.default_meta_data

    def __str__(self):
        return self.message

    @property
    def http_status(self):
        return REASON_TYPE_TO_HTTP_STATUS.get(self.reason_type)


class BlinkValidationError(BlinkError):
    default_message = "A validation error occured"
    default_reason_type = ErrorReasonTypes.validation_error.value


class BlinkConflictError(BlinkError):
    default_message = "A conflict error occured"
    default_reason_type = ErrorReasonTypes.conflict.value


class BlinkParsingError(BlinkError):
    default_message = "A parsing error occured"
    default_reason_type = ErrorReasonTypes.internal_error.value


class ClientError(BlinkError):
    default_message = "A client error occured"
    default_reason_type = ErrorReasonTypes.internal_error.value
