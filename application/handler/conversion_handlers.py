import json
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


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def create_conversion_request(event, context):
    logger.debug(f"create conversion request event={json.dumps(event)}")
    body = get_valid_value(event, HttpRequestParamType.REQUEST_BODY.value)

    if not len(body) or body is None:
        raise BadRequestException(error_code=ErrorCode.MISSING_BODY.value,
                                  error_details=ErrorDetails[ErrorCode.MISSING_BODY.value].value)

    body = json.loads(body)
    validate_schema(filepath="../../documentation/models/conversion.json", schema_key="CreateConversionRequestInput",
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

    amount = Decimal(amount)
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

    validate_schema(filepath="../../documentation/models/conversion.json",
                    schema_key="UpdateConversionHashRequestInput",
                    input_json=body)


if __name__ == "__main__":
    print("welcome boss")
    print(uuid.uuid4().hex)
    body = {
        "token_pair_id": "22477fd4ea994689a04646cbbaafd133",
        "amount": "1333.05",
        "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
        "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
        "block_number": 123456789,
        "signature": "0x2437d4833b185ff1458a21f45bce382f59dfc1d86c38fac53476615513ece5e174381cd44c1bcfe38a6ce30ba67b71dc37ca774d1c3d991ec5fcbf79dca568d81b"
    }
    event = {"body": json.dumps(body)}
    print(create_conversion_request(event, {}))