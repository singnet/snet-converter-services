from enum import Enum


class HttpResponseParamType(Enum):
    STATUS_CODE = "statusCode"
    INVOCATION_TYPE_REQUEST_RESPONSE = "RequestResponse"
    INVOCATION_TYPE_EVENT = "Event"


class HttpRequestParamType(Enum):
    REQUEST_PARAM_QUERY_STRING = 'queryStringParameters'
    REQUEST_PARAM_PATH = 'pathParameters'
    REQUEST_BODY = 'body'
    REQUEST_HEADER = 'headers'
    REQUEST_PARAM_MULTI_VALUE_QUERY_STRING = 'multiValueQueryStringParameters'
    REQUEST_CONTEXT = 'requestContext'


class LambdaResponseStatus(Enum):
    SUCCESS = 'success'
    FAILED = 'failed'


class PaginationDefaults(Enum):
    PAGE_SIZE = 15
    PAGE_NUMBER = 1
    ASC = 'ASC'
