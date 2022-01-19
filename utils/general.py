import json
import uuid
from datetime import datetime

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from common.logger import get_logger
from constants.entity import TokenPairEntities, TokenEntities, BlockchainEntities
from constants.error_details import ErrorCode, ErrorDetails
from utils.exceptions import InternalServerErrorException, BadRequestException

logger = get_logger(__name__)


def get_response_from_entities(list_of_objs):
    return [obj.to_dict() for obj in list_of_objs]


def datetime_to_str(timestamp):
    if not timestamp or timestamp == 'None':
        return ""
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def get_valid_value(dict_name, key):
    val = dict_name.get(key)
    val = {} if val is None else val
    return val


def validate_schema(filepath, schema_key, input_json):
    try:
        f = open(filepath)
        data = json.load(f)
        f.close()
        schema = data.get(schema_key, None)

        if schema is None:
            raise InternalServerErrorException(error_code=ErrorCode.EMPTY_SCHEMA_FILE.value,
                                               error_details=ErrorDetails[ErrorCode.EMPTY_SCHEMA_FILE.value].value)
        validate(instance=input_json, schema=schema)

    except ValidationError as e:
        logger.info(f"Missing required field(s)={e.message}")
        raise BadRequestException(error_code=ErrorCode.SCHEMA_NOT_MATCHING.value,
                                  error_details=ErrorDetails[ErrorCode.SCHEMA_NOT_MATCHING.value].value)
    except Exception as e:
        logger.exception(f"Unexpected error while validating the schema={e}")
        raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_SCHEMA_VALIDATION.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNEXPECTED_ERROR_SCHEMA_VALIDATION.value].value)


def get_uuid():
    return uuid.uuid4().hex


def datetime_in_utcnow():
    return datetime.utcnow()


def get_blockchain_name_from_token_pair_details(token_pair, blockchain_conversion_type):
    if blockchain_conversion_type == TokenPairEntities.FROM_TOKEN.value:
        blockchain = token_pair.get(TokenPairEntities.FROM_TOKEN.value, {}).get(TokenEntities.BLOCKCHAIN.value,
                                                                                {}).get(BlockchainEntities.NAME.value,
                                                                                        None)
    elif blockchain_conversion_type == TokenPairEntities.TO_TOKEN.value:
        blockchain = token_pair.get(TokenPairEntities.TO_TOKEN.value, {}).get(TokenEntities.BLOCKCHAIN.value,
                                                                              {}).get(BlockchainEntities.NAME.value,
                                                                                      None)
    else:
        blockchain = None

    return blockchain
