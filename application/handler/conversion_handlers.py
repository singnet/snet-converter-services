import os
import sys
import json

sys.path.append('/opt')

from web3 import Web3
from http import HTTPStatus

from constants.general import MAX_PAGE_SIZE
from constants.api_parameters import ApiParameters
from constants.lambdas import HttpRequestParamType, LambdaResponseStatus, PaginationDefaults
from constants.error_details import ErrorCode, ErrorDetails
from common.logger import get_logger
from common.utils import generate_lambda_response, make_response_body
from utils.general import get_valid_value, validate_schema
from utils.blockchain import is_valid_cardano_address
from utils.lambdas import make_error_format
from utils.exceptions import BadRequestException, EXCEPTIONS
from utils.exception_handler import exception_handler

from application.service.conversion_service import ConversionService
from application.service.cardano_service import CardanoService
from config import SLACK_HOOK


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
    key = body.get(ApiParameters.KEY.value)

    if not token_pair_id or not amount or not from_address or not to_address or not block_number or not signature:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    response = conversion_service.create_conversion_request(token_pair_id=token_pair_id, amount=amount,
                                                            from_address=from_address, to_address=to_address,
                                                            block_number=block_number, signature=signature, key=key)
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
    address = query_param.get(ApiParameters.ADDRESS.value)
    blockchain_name = query_param.get(ApiParameters.BLOCKCHAIN_NAME.value)
    token_symbol = query_param.get(ApiParameters.TOKEN_SYMBOL.value)
    conversion_status = query_param.get(ApiParameters.CONVERSION_STATUS.value)

    if not address:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    if not Web3.isAddress(address) and not is_valid_cardano_address(address):
        raise BadRequestException(error_code=ErrorCode.INVALID_ADDRESS.value,
                                  error_details=ErrorDetails[ErrorCode.INVALID_ADDRESS.value].value)

    page_size = int(query_param.get(ApiParameters.PAGE_SIZE.value, PaginationDefaults.PAGE_SIZE.value))
    page_number = int(query_param.get(ApiParameters.PAGE_NUMBER.value, PaginationDefaults.PAGE_NUMBER.value))

    if page_size > MAX_PAGE_SIZE:
        raise BadRequestException(error_code=ErrorCode.PAGE_SIZE_EXCEEDS_LIMIT.value,
                                  error_details=ErrorDetails[ErrorCode.PAGE_SIZE_EXCEEDS_LIMIT.value].value)

    response = conversion_service.get_conversion_history(address=address,
                                                         blockchain_name=blockchain_name,
                                                         token_symbol=token_symbol,
                                                         conversion_status=conversion_status,
                                                         page_size=page_size,
                                                         page_number=page_number)

    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value,
                                                       data=response,
                                                       error=make_error_format()),
                                    cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def claim_conversion(event, context):
    logger.debug(f"Claim the conversion request event={json.dumps(event)}")
    path_param = get_valid_value(event, HttpRequestParamType.REQUEST_PARAM_PATH.value)
    body = get_valid_value(event, HttpRequestParamType.REQUEST_BODY.value)

    if not len(body) or body is None:
        raise BadRequestException(error_code=ErrorCode.MISSING_BODY.value,
                                  error_details=ErrorDetails[ErrorCode.MISSING_BODY.value].value)
    conversion_id = path_param.get(ApiParameters.CONVERSION_ID.value, None)
    body = json.loads(body)
    validate_schema(filepath=os.path.dirname(file_path) + "/../../documentation/models/conversion.json",
                    schema_key="ClaimConversionRequestInput", input_json=body)
    amount = body.get(ApiParameters.AMOUNT.value)
    from_address = body.get(ApiParameters.FROM_ADDRESS.value)
    to_address = body.get(ApiParameters.TO_ADDRESS.value)
    signature = body.get(ApiParameters.SIGNATURE.value)

    if not conversion_id or not amount or not from_address or not to_address or not signature:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    response = conversion_service.claim_conversion(conversion_id=conversion_id, amount=amount,
                                                   from_address=from_address, to_address=to_address,
                                                   signature=signature)
    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_conversion(event, context):
    logger.debug(f"Get conversion request event={json.dumps(event)}")
    path_param = get_valid_value(event, HttpRequestParamType.REQUEST_PARAM_PATH.value)
    conversion_id = path_param.get(ApiParameters.CONVERSION_ID.value)

    if not conversion_id:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    response = conversion_service.get_conversion(conversion_id=conversion_id)
    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_conversion_count_by_status(event, context):
    logger.debug(f"Get conversion count by status event={json.dumps(event)}")
    validate_schema(filepath=os.path.dirname(file_path) + "/../../documentation/models/conversion.json",
                    schema_key="GetConversionStatusCountInput", input_json=event)

    query_param = get_valid_value(event, HttpRequestParamType.REQUEST_PARAM_QUERY_STRING.value)
    address = query_param.get(ApiParameters.ADDRESS.value, None)

    if not address:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    if not Web3.isAddress(address) and not is_valid_cardano_address(address):
        raise BadRequestException(error_code=ErrorCode.INVALID_ADDRESS.value,
                                  error_details=ErrorDetails[ErrorCode.INVALID_ADDRESS.value].value)

    response = conversion_service.get_conversion_count_by_status(address=address)

    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_transaction_by_conversion_id(event, context):
    logger.debug(f"Getting the transactions for the conversion event request={json.dumps(event)}")
    validate_schema(filepath=os.path.dirname(file_path) + "/../../documentation/models/conversion.json",
                    schema_key="GetTransactionByConversionInput", input_json=event)

    query_param = get_valid_value(event, HttpRequestParamType.REQUEST_PARAM_QUERY_STRING.value)
    conversion_id = query_param.get(ApiParameters.CONVERSION_ID.value, None)

    if not conversion_id:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY.value,
                                  error_details=ErrorDetails[ErrorCode.PROPERTY_VALUES_EMPTY.value].value)

    response = conversion_service.get_transaction_by_conversion_id(conversion_id=conversion_id)
    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_converter_liquidity_balance(event, context):
    logger.debug(f"Getting the liquid balance for the conversion event request={json.dumps(event)}")
    validate_schema(filepath=os.path.dirname(file_path) + "/../../documentation/models/conversion.json",
                    schema_key="GetLiquidityDataInput", input_json=event)

    query_param = get_valid_value(event, HttpRequestParamType.REQUEST_PARAM_QUERY_STRING.value)
    token_pair_id = query_param.get(ApiParameters.TOKEN_PAIR_ID.value, None)

    if not token_pair_id:
        raise BadRequestException(error_code=ErrorCode.PROPERTY_VALUES_EMPTY)

    response = conversion_service.get_liquidity_balance_data(token_pair_id)

    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_converter_liquidity_addresses(event, context):
    logger.debug(f"Getting the liquidity addresses :: {json.dumps(event)}")

    response = CardanoService().get_liquidity_addresses()

    return generate_lambda_response(HTTPStatus.OK.value,
                                    make_response_body(status=LambdaResponseStatus.SUCCESS.value, data=response,
                                                       error=make_error_format()), cors_enabled=True)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def expire_conversion(event, context):
    logger.debug(f"Job for expiring the conversion request={json.dumps(event)}")
    conversion_service.expire_conversion()
    logger.info("Successfully")


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def generate_conversion_report(event, context):
    logger.debug(f"Generating the conversion report request={json.dumps(event)}")
    conversion_service.generate_conversion_report()
    logger.info("Successfully")
