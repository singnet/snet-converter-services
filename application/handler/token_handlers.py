import json
from http import HTTPStatus

from common.logger import get_logger
from common.utils import generate_lambda_response, make_response_body
from config import SLACK_HOOK
from constants.lambdas import LambdaResponseStatus
from utils.exception_handler import exception_handler
from utils.exceptions import EXCEPTIONS
from utils.lambdas import make_error_format

logger = get_logger(__name__)
token_service = TokenService()


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_token_pair(event, context):
    logger.debug(f"Get all token pair event={json.dumps(event)}")
    response = token_service.get_token_pair()
    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)

