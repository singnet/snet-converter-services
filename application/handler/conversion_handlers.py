import json
import os
import sys
import uuid
from decimal import Decimal

from config import SLACK_HOOK
from constants.error_details import ErrorCode, ErrorDetails
from utils.exception_handler import exception_handler

sys.path.append('/opt')
from http import HTTPStatus

from application.service.conversion_service import ConversionService
from common.logger import get_logger
from common.utils import logger, generate_lambda_response, make_response_body
from constants.api_parameters import ApiParameters
from utils.lambdas import make_error_format

from constants.lambdas import HttpRequestParamType, LambdaResponseStatus
from utils.exceptions import BadRequestException, EXCEPTIONS
from utils.general import get_valid_value, validate_schema

logger = get_logger(__name__)

conversion_service = ConversionService()
file_path = os.path.realpath(__file__)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def create_conversion_request(event, context):
    logger.debug(f"create conversion request event={json.dumps(event)}")
    body = get_valid_value(event, HttpRequestParamType.REQUEST_BODY.value)

    if not len(body) or body is None:
        raise BadRequestException(error_code=ErrorCode.MISSING_BODY.value,
                                  error_details=ErrorDetails[ErrorCode.MISSING_BODY.value].value)

    body = json.loads(body)
    validate_schema(filepath=os.path.dirname(file_path)+"/../../documentation/models/conversion.json", schema_key="CreateConversionRequestInput",
                    input_json=body)
    token_pair_id = body.get(ApiParameters.TOKEN_PAIR_ID.value)
    amount = body.get(ApiParameters.AMOUNT.value)
    from_address = body.get(ApiParameters.FROM_ADDRESS.value)
    to_address = body.get(ApiParameters.TO_ADDRESS.value)
    block_number = body.get(ApiParameters.BLOCK_NUMBER.value)
    signature = body.get(ApiParameters.SIGNATURE.value)

    if not token_pair_id or not amount or not from_address or not to_address or not block_number or not signature:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    response = conversion_service.create_conversion_request(token_pair_id=token_pair_id, amount=amount,
                                                            from_address=from_address, to_address=to_address,
                                                            block_number=block_number, signature=signature)
    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def update_conversion_hash(event, context):
    logger.debug(f"Updating the conversion hash event={json.dumps(event)}")
    body = get_valid_value(event, HttpRequestParamType.REQUEST_BODY.value)

    if body is None:
        raise BadRequestException(error_code=ErrorCode.BAD_REQUEST.value, error_details="Missing body")

    body = json.loads(body)

    validate_schema(filepath=os.getcwd() + "/../../documentation/models/conversion.json",
                    schema_key="UpdateConversionHashRequestInput",
                    input_json=body)

