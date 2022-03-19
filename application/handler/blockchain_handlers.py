import sys

sys.path.append('/opt')
import json

from http import HTTPStatus

from application.service.blockchain_service import BlockchainService
from common.logger import get_logger
from common.utils import generate_lambda_response, make_response_body
from config import SLACK_HOOK
from constants.lambdas import LambdaResponseStatus

from utils.exception_handler import exception_handler
from utils.exceptions import EXCEPTIONS
from utils.lambdas import make_error_format

logger = get_logger(__name__)
blockchain_service = BlockchainService()


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_all_blockchain(event, context):
    logger.debug(f"Get blockchain event={json.dumps(event)}")
    response = blockchain_service.get_all_blockchain()
    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)
