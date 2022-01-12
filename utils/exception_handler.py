import sys
import traceback
import time
from http import HTTPStatus

from common.utils import generate_lambda_response, make_response_body, Utils
from constants.lambdas import HttpRequestParamType, LambdaResponseStatus
from utils.exceptions import InternalServerErrorException
from utils.lambdas import make_error_format

utils_obj = Utils()
internal_server_exception_obj = InternalServerErrorException(error_code=None, error_details=None)


def exception_handler(*decorator_args, **decorator_kwargs):
    logger = decorator_kwargs["logger"]

    def decorator(func):
        NETWORK_ID = decorator_kwargs.get("NETWORK_ID", None)
        SLACK_HOOK = decorator_kwargs.get("SLACK_HOOK", None)
        EXCEPTIONS = decorator_kwargs.get("EXCEPTIONS", ())

        def get_exec_info():
            exec_info = sys.exc_info()
            formatted_exec_info = traceback.format_exception(*exec_info)
            exception_info = ""
            for exc_lines in formatted_exec_info:
                exception_info = exception_info + exc_lines
            return exception_info

        def wrapper(*args, **kwargs):
            event = kwargs.get("event", args[0])
            now = time.time()

            handler_name = decorator_kwargs.get("handler_name", func.__name__)
            path = event.get("path", None)
            headers = event.get(HttpRequestParamType.REQUEST_HEADER.value, {})
            path_parameters = event.get(HttpRequestParamType.REQUEST_PARAM_PATH.value, {})
            query_string_parameters = event.get(HttpRequestParamType.REQUEST_PARAM_QUERY_STRING.value, {})
            body = event.get(HttpRequestParamType.REQUEST_BODY.value, "{}")

            error_message = f"Error Reported! \n" \
                            f"network_id: {NETWORK_ID}\n" \
                            f"path: {path}, \n" \
                            f"handler: {handler_name} \n" \
                            f"header: {headers} \n" \
                            f"pathParameters: {path_parameters} \n" \
                            f"queryStringParameters: {query_string_parameters} \n" \
                            f"body: {body} \n" \
                            f"error_description: \n"

            try:
                func_response = func(*args, **kwargs)
                later = time.time()
                difference = int(later - now)

                logger.info(f"Time taken for handler name= {handler_name} time={difference} seconds")
                return func_response
            except EXCEPTIONS as e:
                exec_info = get_exec_info()
                slack_message = f"```{error_message}{exec_info}```"

                if e.status_code != HTTPStatus.BAD_REQUEST.value:
                    logger.exception(slack_message)
                    utils_obj.report_slack(slack_msg=slack_message, SLACK_HOOK=SLACK_HOOK)
                else:
                    logger.debug(slack_message)

                return generate_lambda_response(
                    e.status_code,
                    make_response_body(status=e.status, data=None,
                                       error=make_error_format(error_code=e.error_code, error_message=e.error_message,
                                                               error_details=e.error_details)), cors_enabled=True)
            except Exception as e:
                exec_info = get_exec_info()
                slack_message = f"```{error_message}{exec_info}```"
                logger.exception(slack_message)

                utils_obj.report_slack(slack_msg=slack_message, SLACK_HOOK=SLACK_HOOK)

                return generate_lambda_response(
                    internal_server_exception_obj.status_code,
                    make_response_body(status=LambdaResponseStatus.FAILED.value, data=None,
                                       error=make_error_format(error_code=internal_server_exception_obj.error_code,
                                                               error_message=internal_server_exception_obj.error_message,
                                                               error_details=repr(e))), cors_enabled=True)

        return wrapper

    return decorator
