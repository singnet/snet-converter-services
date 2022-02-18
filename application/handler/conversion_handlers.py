import json
import os
import sys

sys.path.append('/opt')
import uuid

from config import SLACK_HOOK
from constants.error_details import ErrorCode, ErrorDetails
from utils.exception_handler import exception_handler

from http import HTTPStatus

from application.service.conversion_service import ConversionService
from common.logger import get_logger
from common.utils import generate_lambda_response, make_response_body
from constants.api_parameters import ApiParameters
from utils.lambdas import make_error_format

from constants.lambdas import HttpRequestParamType, LambdaResponseStatus, PaginationDefaults
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
    validate_schema(filepath=os.path.dirname(file_path) + "/../../documentation/models/conversion.json",
                    schema_key="CreateConversionRequestInput", input_json=body)
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
def create_transaction_for_conversion(event, context):
    logger.debug(f"Update conversion request event={json.dumps(event)}")
    body = get_valid_value(event, HttpRequestParamType.REQUEST_BODY.value)

    if not len(body) or body is None:
        raise BadRequestException(error_code=ErrorCode.MISSING_BODY.value,
                                  error_details=ErrorDetails[ErrorCode.MISSING_BODY.value].value)

    body = json.loads(body)
    validate_schema(filepath=os.path.dirname(file_path) + "/../../documentation/models/conversion.json",
                    schema_key="CreateTransactionForConversionInput", input_json=body)

    conversion_id = body.get(ApiParameters.CONVERSION_ID.value)
    transaction_hash = body.get(ApiParameters.TRANSACTION_HASH.value)

    if not conversion_id or not transaction_hash:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    response = conversion_service.create_transaction_for_conversion(conversion_id=conversion_id,
                                                                    transaction_hash=transaction_hash)

    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_conversion_history(event, context):
    logger.debug(f"Conversion history request event={json.dumps(event)}")

    validate_schema(filepath=os.path.dirname(file_path) + "/../../documentation/models/conversion.json",
                    schema_key="GetConversionHistoryInput", input_json=event)

    query_param = get_valid_value(event, HttpRequestParamType.REQUEST_PARAM_QUERY_STRING.value)
    address = query_param.get(ApiParameters.ADDRESS.value, None)

    if not address:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    page_size = int(query_param.get(ApiParameters.PAGE_SIZE.value, PaginationDefaults.PAGE_SIZE.value))
    page_number = int(query_param.get(ApiParameters.PAGE_NUMBER.value, PaginationDefaults.PAGE_NUMBER.value))

    response = conversion_service.get_conversion_history(address=address, page_size=page_size, page_number=page_number)

    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)





if __name__ == "__main__":
    print("welcome boss")
    print(uuid.uuid4().hex)
    body = {
        "conversion_id": "5086b5245cd046a68363d9ca8ed0027e",
        "transaction_hash": "0xe5bd9472b9d9931ca41bc3598f2ec15665b77ef32c088da5f2f8f3d2f72782a9",
        "token_pair_id": "22477fd4ea994689a04646cbbaafd133",
        "amount": "1333.05",
        "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
        "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
        "block_number": 12345678,
        "signature": "0xd4159d88ccc844ced5f0fa19b2975877813ab82f5c260d8cbacc1c11e9d61e8c776db78473a052ee02da961e98c7326f70c5e37e9caa2240dbb17baea2d4c69c1b"
    }
    event = {"body": json.dumps(body),
             "queryStringParameters": {"address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1"}}
    print(converter_event_consumer(event, {}))
