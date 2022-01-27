import math
from decimal import Decimal

from web3.exceptions import TransactionNotFound

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from config import CARDANO_DEPOSIT_ADDRESS
from constants.entity import BlockchainEntities, TokenEntities, ConversionDetailEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, MAX_ALLOWED_DECIMAL, ConversionOn
from utils.cardano_blockchain import get_blockfrost_api_object
from utils.exceptions import InternalServerErrorException, BadRequestException
from utils.general import get_ethereum_network_url, validate_conversion_with_blockchain, \
    get_cardano_network_url_and_project_id, check_existing_transaction_succeed, is_supported_chain_id

logger = get_logger(__name__)


def get_deposit_address(blockchain_name):
    deposit_address = None
    if blockchain_name == BlockchainName.CARDANO.value:
        deposit_address = get_cardano_deposit_address()

    return deposit_address


def get_cardano_deposit_address():
    """
    TODO: call cardano cli web to get the public address
    """
    return CARDANO_DEPOSIT_ADDRESS


def validate_cardano_address(address, chain_ids):
    chain_ids


def validate_address(from_address, to_address, from_blockchain, to_blockchain):
    logger.info(f"validating the input address from_address={from_address}, from_blockchain={from_blockchain}"
                f", to_adress={to_address}, to_blockchain_name={to_blockchain}")
    from_blockchain_name = from_blockchain.get(BlockchainEntities.NAME.value)
    from_blockchain_chain_id = from_blockchain.get(BlockchainEntities.CHAIN_ID.value)

    to_blockchain_name = to_blockchain.get(BlockchainEntities.NAME.value)
    to_blockchain_chain_id = to_blockchain.get(BlockchainEntities.NAME.value)

    if from_blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
        validate_cardano_address(address=from_address, chain_ids=from_blockchain_chain_id)

    if to_blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
        validate_cardano_address(address=to_address, chain_ids=to_blockchain_chain_id)


def get_lowest_unit_amount(amount, allowed_decimal):
    if allowed_decimal is None or allowed_decimal <= 0:
        return Decimal(amount)

    if allowed_decimal > MAX_ALLOWED_DECIMAL:
        raise InternalServerErrorException(error_code=ErrorCode.ALLOWED_DECIMAL_LIMIT_EXISTS.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.ALLOWED_DECIMAL_LIMIT_EXISTS.value].value)
    return Decimal(amount) * Decimal(math.pow(10, allowed_decimal))


def validate_ethereum_transaction_details_against_conversion(chain_id, transaction_hash, conversion_on,
                                                             conversion_detail):
    network_url = get_ethereum_network_url(chain_id=chain_id)
    ethereum_web3_object = BlockChainUtil(provider_type="HTTP_PROVIDER", provider=network_url)
    try:
        blockchain_transaction = ethereum_web3_object.get_transaction_receipt_from_blockchain(
            transaction_hash=transaction_hash)

        if not validate_conversion_with_blockchain(conversion_on=conversion_on,
                                                   address=blockchain_transaction.get("from"),
                                                   amount=None, conversion_detail=conversion_detail):
            raise BadRequestException(error_code=ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value,
                                      error_details=ErrorDetails[
                                          ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value].value)

    except TransactionNotFound as e:
        raise BadRequestException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)
    except Exception as e:
        raise InternalServerErrorException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)


def validate_cardano_transaction_details_against_conversion(chain_id, transaction_hash, conversion_on,
                                                            conversion_detail):
    url, project_id = get_cardano_network_url_and_project_id(chain_id=chain_id)
    blockfrost_api = get_blockfrost_api_object(project_id=project_id, base_url=url)
    try:
        blockchain_transaction = blockfrost_api.transaction_utxos(hash=transaction_hash)

        if not validate_conversion_with_blockchain(conversion_on=conversion_on,
                                                   address=blockchain_transaction.inputs[0].address,
                                                   amount=None, conversion_detail=conversion_detail):
            raise BadRequestException(error_code=ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value,
                                      error_details=ErrorDetails[
                                          ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value].value)
    except Exception as e:
        logger.info(repr(e))
        raise BadRequestException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)


def validate_transaction_hash(conversion_detail, transaction_hash):
    transaction = conversion_detail.get("transaction")

    if not len(transaction):
        conversion_on = ConversionOn.FROM.value
        blockchain = conversion_detail.get(ConversionDetailEntities.FROM_TOKEN.value).get(
            TokenEntities.BLOCKCHAIN.value)
    else:
        if not check_existing_transaction_succeed(transaction):
            raise BadRequestException(error_code=ErrorCode.EXISTING_TRANSACTION_IS_NOT_SUCCEEDED.value,
                                      error_details=ErrorDetails[
                                          ErrorCode.EXISTING_TRANSACTION_IS_NOT_SUCCEEDED.value].value)

        conversion_on = ConversionOn.TO.value
        blockchain = conversion_detail.get(ConversionDetailEntities.TO_TOKEN.value).get(
            TokenEntities.BLOCKCHAIN.value)

    blockchain_name = blockchain.get("name").lower()
    chain_id = blockchain.get("chain_id")

    if not is_supported_chain_id(blockchain_type=blockchain_name, chain_id=chain_id):
        logger.exception(f"Unsupported chain id configured for the blockchain name={blockchain_name} "
                         f"with chain_id={chain_id}")
        raise InternalServerErrorException(error_code=ErrorCode.UNSUPPORTED_CHAIN_ID.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNSUPPORTED_CHAIN_ID.value].value)

    if blockchain_name == BlockchainName.ETHEREUM.value.lower():
        validate_ethereum_transaction_details_against_conversion(chain_id=chain_id,
                                                                 transaction_hash=transaction_hash,
                                                                 conversion_on=conversion_on,
                                                                 conversion_detail=conversion_detail)
    elif blockchain_name == BlockchainName.CARDANO.value.lower():
        validate_cardano_transaction_details_against_conversion(chain_id=chain_id,
                                                                transaction_hash=transaction_hash,
                                                                conversion_on=conversion_on,
                                                                conversion_detail=conversion_detail)
