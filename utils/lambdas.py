def make_error_format(error_code=None, error_message=None, error_details=None):
    return {
        "code": error_code,
        "message": error_message,
        "details": error_details
    }
