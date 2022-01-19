from enum import Enum


class ErrorCode(Enum):
    MISSING_BODY = "E0001"
    EMPTY_SCHEMA_FILE = "E0002"
    SCHEMA_NOT_MATCHING = "E0003"
    UNEXPECTED_ERROR_SCHEMA_VALIDATION = "E0004"
    PROPERTY_VALUES_EMPTY = "E0005"
    INCORRECT_SIGNATURE = "E0006"
    ALLOWED_DECIMAL_LIMIT_EXISTS = "E0007"


class ErrorDetails(Enum):
    E0001 = "Missing body"
    E0002 = "Schema is Empty"
    E0003 = "Schema is not matching with request"
    E0004 = "Unexpected error occurred during schema validation"
    E0005 = "Property value is empty"
    E0006 = "Incorrect signature provided"
    E0007 = "Allowed decimal limit exists"

