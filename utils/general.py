import json
import math
import uuid
from datetime import datetime

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from common.logger import get_logger
from config import BLOCKCHAIN_DETAILS
from constants.blockchain import EthereumSupportedNetwork, CardanoSupportedNetwork, EthereumNetwork, CardanoNetwork
from constants.entity import TokenPairEntities, TokenEntities, BlockchainEntities, PaginationEntity, \
    ConversionDetailEntities, WalletPairEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, ConversionOn
from constants.lambdas import PaginationDefaults
from constants.status import TransactionStatus
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


def get_blockchain_from_token_pair_details(token_pair, blockchain_conversion_type):
    if blockchain_conversion_type == TokenPairEntities.FROM_TOKEN.value:
        blockchain = token_pair.get(TokenPairEntities.FROM_TOKEN.value, {}).get(TokenEntities.BLOCKCHAIN.value,
                                                                                {})
    elif blockchain_conversion_type == TokenPairEntities.TO_TOKEN.value:
        blockchain = token_pair.get(TokenPairEntities.TO_TOKEN.value, {}).get(TokenEntities.BLOCKCHAIN.value,
                                                                              {})
    else:
        blockchain = None

    return blockchain


def get_offset(page_number, page_size):
    return (page_number - 1) * page_size


def paginate_items(items, page_number, page_size):
    page_size = PaginationDefaults.PAGE_SIZE.value if page_size == 0 else page_size
    total_records = len(items)
    start_length = get_offset(page_number=page_number, page_size=page_size)
    end_length = page_number * page_size
    paginated_items = items[start_length:end_length]
    return paginate_items_response_format(items=paginated_items, total_records=total_records, page_number=page_number,
                                          page_size=page_size)


def paginate_items_response_format(items, total_records, page_number, page_size):
    return {PaginationEntity.ITEMS.value: items,
            PaginationEntity.META.value: {PaginationEntity.TOTAL_RECORDS.value: total_records,
                                          PaginationEntity.PAGE_COUNT.value: math.ceil(
                                              float(total_records) / page_size),
                                          PaginationEntity.PAGE_NUMBER.value: page_number,
                                          PaginationEntity.PAGE_SIZE.value: page_size}}


def check_existing_transaction_succeed(transaction):
    is_check_existing_transaction_succeed = True
    for x in transaction:
        status = x.get("status")
        id = x.get("id")
        if status != TransactionStatus.SUCCESS.value:
            logger.info(f"Transaction is not success for the transaction_id={id} having a status={status}")
            is_check_existing_transaction_succeed = False
            break
    return is_check_existing_transaction_succeed


def is_supported_chain_id(blockchain_type, chain_id):
    is_supported = False

    if blockchain_type == BlockchainName.ETHEREUM.value.lower() and chain_id in EthereumSupportedNetwork:
        is_supported = True
    elif blockchain_type == BlockchainName.CARDANO.value.lower() and chain_id in CardanoSupportedNetwork:
        is_supported = True

    return is_supported


def get_ethereum_network_url(chain_id):
    network_name = EthereumNetwork(chain_id).name
    url = BLOCKCHAIN_DETAILS.get(BlockchainName.ETHEREUM.value.lower(), {}).get("network", {}).get(network_name.lower(),
                                                                                                   {}).get("url", None)
    if url is None:
        raise "Url not found from config"

    return url


def get_cardano_network_url_and_project_id(chain_id):
    network_name = CardanoNetwork(chain_id).name
    network_config = BLOCKCHAIN_DETAILS.get(BlockchainName.CARDANO.value.lower(), {}).get("network", {}).get(
        network_name.lower(), {})
    url = network_config.get("url", None)
    project_id = network_config.get("secret", {}).get("project_id", None)

    if url is None or project_id is None:
        raise "Url not found from config"

    return url, project_id


def validate_conversion_with_blockchain(conversion_on, address, amount, conversion_detail):
    logger.info(
        f"Validating the conversion with blockchain details conversion_on={conversion_on}, address={address}, amount={amount}")
    is_valid = False

    if conversion_on == ConversionOn.FROM.value and address == conversion_detail.get(
            ConversionDetailEntities.WALLET_PAIR.value, {}).get(WalletPairEntities.FROM_ADDRESS.value):
        is_valid = True
    elif conversion_on == ConversionOn.TO.value and address == conversion_detail.get(
            ConversionDetailEntities.WALLET_PAIR.value, {}).get(WalletPairEntities.TO_ADDRESS.value):
        is_valid = True

    return is_valid
