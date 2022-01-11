from http import HTTPStatus

from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response, make_response_body
from config import SLACK_HOOK

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_blockchain(event, context):
    response = {"test": "welcome"}
    return generate_lambda_response(HTTPStatus.OK.value, make_response_body(response, ""), cors_enabled=True)
