class AccessDeniedException(Exception):
    error_message = "ACCESS_DENIED"
    status_code = 401

    def __init__(self, error_code, error_details):
        self.error_code = error_code
        self.error_details = error_details


class BadRequestException(Exception):
    status_code = 400
    error_message = "BAD_REQUEST"

    def __init__(self, error_code, error_details):
        self.error_code = error_code
        self.error_details = error_details


class InternalServerErrorException(Exception):
    error_message = "INTERNAL_SERVER_ERROR"
    status_code = 500

    def __init__(self, error_code, error_details):
        self.error_code = error_code
        self.error_details = error_details


EXCEPTIONS = (AccessDeniedException, BadRequestException, InternalServerErrorException)
