from constants.error_details import ErrorCode, ErrorDetails


class CustomConverterException(Exception):
    status_code = 500
    error_message = "INTERNAL_SERVER_ERROR"

    def __init__(self, error_code, error_details=None):

        self.error_code = error_code
        self.error_details = error_details

        # Simplify passing of standard error codes
        if isinstance(error_code, ErrorCode):
            self.error_code = error_code.value
            if error_details is None:
                self.error_details = ErrorDetails[self.error_code].value


class AccessDeniedException(CustomConverterException):
    status_code = 401
    error_message = "ACCESS_DENIED"


class BadRequestException(CustomConverterException):
    status_code = 400
    error_message = "BAD_REQUEST"


class InternalServerErrorException(CustomConverterException):
    status_code = 500
    error_message = "INTERNAL_SERVER_ERROR"


class TokenPairIdNotExitsException(CustomConverterException):
    status_code = 400
    error_message = "BAD_REQUEST"


class BlockConfirmationNotEnoughException(CustomConverterException):
    status_code = 500
    error_message = "NOT_ENOUGH_BLOCK_CONFIRMATION"


EXCEPTIONS = (AccessDeniedException, BadRequestException, InternalServerErrorException, TokenPairIdNotExitsException)
