import json
import math
import uuid
from datetime import datetime
from datetime import timedelta
from decimal import Decimal, ROUND_DOWN

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from common.logger import get_logger
from config import BLOCKCHAIN_DETAILS
from constants.blockchain import EthereumSupportedNetwork, CardanoSupportedNetwork, EthereumNetwork, CardanoNetwork, \
    EthereumEnvironment, CardanoEnvironment, BinanceSupportedNetwork, BinanceNetwork, BinanceEnvironment
from constants.entity import TokenPairEntities, TokenEntities, BlockchainEntities, PaginationEntity, \
    TransactionEntities, ConversionReportingEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName
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
    return dict_name.get(key, {})


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


def relative_date(date_time: datetime, hours: int = 0, days: int = 0) -> datetime:
    return date_time - timedelta(hours=int(hours), days=int(days))


def reset_decimal_places(amount: Decimal, from_decimals: int, to_decimals: int) -> Decimal:
    """
    Resets to zero redundant decimal places of the amount when from_decimals exceeds to_decimals
    """
    if from_decimals > to_decimals:
        factor = 10 ** (from_decimals - to_decimals)
        return amount // factor * factor
    return amount


def update_decimal_places(amount: Decimal, from_decimals: int, to_decimals: int) -> Decimal:
    """
    Updates number of decimal places of the amount depending on difference of the from_decimals and to_decimals
    """
    if to_decimals > from_decimals:
        factor = 10 ** (to_decimals - from_decimals)
        return amount * factor
    if from_decimals > to_decimals:
        factor = 10 ** (from_decimals - to_decimals)
        return amount // factor
    return amount


def calculate_fee_amount(amount: Decimal, percentage: str) -> Decimal:
    percentage_decimal = Decimal(percentage) / 100
    fee_amount = amount * percentage_decimal
    fee_amount = fee_amount.quantize(Decimal("1."), rounding=ROUND_DOWN)
    return fee_amount


def calculate_claim_amount_by_conversion_ratio(amount: Decimal, conversion_ratio: Decimal):
    claim_amount = amount * conversion_ratio
    claim_amount = claim_amount.quantize(Decimal("1."), rounding=ROUND_DOWN)
    return claim_amount


def get_blockchain_from_token_pair_details(token_pair, blockchain_conversion_type):
    if blockchain_conversion_type == TokenPairEntities.FROM_TOKEN.value:
        blockchain = token_pair.get(TokenPairEntities.FROM_TOKEN.value, {}) \
                               .get(TokenEntities.BLOCKCHAIN.value, {})
    elif blockchain_conversion_type == TokenPairEntities.TO_TOKEN.value:
        blockchain = token_pair.get(TokenPairEntities.TO_TOKEN.value, {}) \
                               .get(TokenEntities.BLOCKCHAIN.value, {})
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
            PaginationEntity.META.value: {
                PaginationEntity.TOTAL_RECORDS.value: total_records,
                PaginationEntity.PAGE_COUNT.value: math.ceil(float(total_records) / page_size),
                PaginationEntity.PAGE_NUMBER.value: page_number,
                PaginationEntity.PAGE_SIZE.value: page_size}}


def check_existing_transaction_succeed(transactions):
    is_check_existing_transaction_succeed = True
    for transaction in transactions:
        status = transaction.get(TransactionEntities.STATUS.value)
        id_ = transaction.get(TransactionEntities.ID.value)
        if status != TransactionStatus.SUCCESS.value:
            logger.info(f"Transaction is not success for the transaction_id={id_} having a status={status}")
            is_check_existing_transaction_succeed = False
            break

    return is_check_existing_transaction_succeed


def get_transactions_operation(transactions):
    return [transaction.get(TransactionEntities.TRANSACTION_OPERATION.value) for transaction in transactions]


def is_supported_chain_id(blockchain_name, chain_id):
    is_supported = False

    if blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower() and chain_id in EthereumSupportedNetwork:
        is_supported = True
    elif blockchain_name.lower() == BlockchainName.BINANCE.value.lower() and chain_id in BinanceSupportedNetwork:
        is_supported = True
    elif blockchain_name.lower() == BlockchainName.CARDANO.value.lower() and chain_id in CardanoSupportedNetwork:
        is_supported = True

    return is_supported


def get_chain_environment(blockchain_name, chain_id):
    environment = None
    if blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower():
        environment = EthereumEnvironment[EthereumNetwork(chain_id).name].value
    elif blockchain_name.lower() == BlockchainName.BINANCE.value.lower():
        environment = BinanceEnvironment[BinanceNetwork(chain_id).name].value
    elif blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
        environment = CardanoEnvironment[CardanoNetwork(chain_id).name].value

    return environment


def is_supported_network_conversion(from_blockchain, to_blockchain):
    is_supported = False
    from_blockchain_name = from_blockchain.get(BlockchainEntities.NAME.value)
    from_chain_id = from_blockchain.get(BlockchainEntities.CHAIN_ID.value)
    to_blockchain_name = to_blockchain.get(BlockchainEntities.NAME.value)
    to_chain_id = to_blockchain.get(BlockchainEntities.CHAIN_ID.value)

    if is_supported_chain_id(blockchain_name=from_blockchain_name, chain_id=from_chain_id) and \
            is_supported_chain_id(blockchain_name=to_blockchain_name, chain_id=to_chain_id) and \
            get_chain_environment(blockchain_name=from_blockchain_name, chain_id=from_chain_id) == \
            get_chain_environment(blockchain_name=to_blockchain_name, chain_id=to_chain_id):
        is_supported = True

    return is_supported


def get_evm_blockchain(chain_id):
    if chain_id in [network.value for network in EthereumNetwork]:
        return BlockchainName.ETHEREUM.value
    elif chain_id in [network.value for network in BinanceNetwork]:
        return BlockchainName.BINANCE.value
    else:
        raise ValueError(f"EVM chain id {chain_id} is not supported")


def get_evm_network_url(chain_id):
    if chain_id in [network.value for network in EthereumNetwork]:
        return get_ethereum_network_url(chain_id)
    elif chain_id in [network.value for network in BinanceNetwork]:
        return get_binance_network_url(chain_id)
    else:
        raise ValueError(f"EVM chain id {chain_id} is not supported")


def get_ethereum_network_url(chain_id):
    network_name = EthereumNetwork(chain_id).name
    url = BLOCKCHAIN_DETAILS.get(BlockchainName.ETHEREUM.value.lower(), {}) \
                            .get("network", {}) \
                            .get(network_name.lower(), {}) \
                            .get("url", None)
    assert url is not None, "Url not found from config"
    return url


def get_binance_network_url(chain_id):
    network_name = BinanceNetwork(chain_id).name
    url = BLOCKCHAIN_DETAILS.get(BlockchainName.BINANCE.value.lower(), {}) \
                            .get("network", {}) \
                            .get(network_name.lower(), {}) \
                            .get("url", None)
    assert url is not None, "Url not found from config"
    return url


def get_cardano_network_url_and_project_id(chain_id):
    network_name = CardanoNetwork(chain_id).name
    network_config = BLOCKCHAIN_DETAILS.get(BlockchainName.CARDANO.value.lower(), {}) \
                                       .get("network", {}) \
                                       .get(network_name.lower(), {})
    url = network_config.get("url", None)
    project_id = network_config.get("secret", {}).get("project_id", None)
    assert url is not None, "Url not found from config"
    assert project_id is not None, "Project ID not found"
    return url, project_id


def string_to_bytes_to_hex(message):
    return f"0x{message.encode('utf-8').hex()}"


def get_formatted_conversion_status_report(start_date, end_date, report):
    content = "\nHey there :wave: \n ********************************************************************************"
    content = content + f"\nConversion Report from :timer_clock: {start_date} to {end_date} :timer_clock:"
    content = content + "\n********************************************************************************"
    content = content + "\nFrom BC\tTo BC\tToken\tConversion Count\tConversion Count by Status"
    content = content + "\n---------------------------------------------------------------------------------------"
    for key, value in report.items():
        from_blockchain = value.get(ConversionReportingEntities.FROM_BLOCKCHAIN.value)
        to_blockchain = value.get(ConversionReportingEntities.TO_BLOCKCHAIN.value)
        token = value.get(ConversionReportingEntities.TOKEN.value)
        total_count = value.get(ConversionReportingEntities.TOTAL_CONVERSION.value)
        each_count = value.get(ConversionReportingEntities.EACH_CONVERSION.value)
        content = content + f"\n{from_blockchain}\t{to_blockchain}\t{token}\t{total_count}\t{each_count}"
    content = content + "\n------------------------------- Done :white_check_mark: -------------------------------\n"
    return content
