import json
import sys

sys.path.append('/opt')
from http import HTTPStatus

from constants.general import ETHEREUM_WALLET_ADDRESS_LENGTH
from application.service.wallet_pair_service import WalletPairService
from common.logger import get_logger
from common.utils import generate_lambda_response, make_response_body
from config import SLACK_HOOK
from constants.api_parameters import ApiParameters
from constants.error_details import ErrorCode, ErrorDetails
from constants.lambdas import HttpRequestParamType, LambdaResponseStatus
from utils.exception_handler import exception_handler
from utils.exceptions import EXCEPTIONS, BadRequestException
from utils.general import get_valid_value
from utils.lambdas import make_error_format

logger = get_logger(__name__)

wallet_service = WalletPairService()


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_wallets_address_by_ethereum_address(event, context):
    logger.debug(f"Get the wallet address request event={json.dumps(event)}")
    query_param = get_valid_value(event, HttpRequestParamType.REQUEST_PARAM_QUERY_STRING.value)
    ethereum_address = query_param.get(ApiParameters.ETHEREUM_ADDRESS.value)

    if not ethereum_address:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    if len(ethereum_address) != ETHEREUM_WALLET_ADDRESS_LENGTH:
        raise BadRequestException(error_code=ErrorCode.INVALID_ETHEREUM_ADDRESS.value,
                                  error_details=ErrorDetails[ErrorCode.INVALID_ETHEREUM_ADDRESS.value].value)

    response = wallet_service.get_wallets_address_by_ethereum_address(ethereum_address=ethereum_address)
    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_all_deposit_address(event, context):
    logger.debug(f"Getting all the deposit address request event={json.dumps(event)}")
    response = wallet_service.get_all_deposit_address()
    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)
