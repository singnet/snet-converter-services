import math
from decimal import Decimal
from http import HTTPStatus

from web3.exceptions import TransactionNotFound

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from config import CARDANO_DEPOSIT_ADDRESS
from constants.entity import BlockchainEntities, TokenEntities, ConversionDetailEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, MAX_ALLOWED_DECIMAL, ConversionOn
from constants.status import TransactionOperation
from utils.cardano_blockchain import CardanoBlockchainUtil
from utils.exceptions import InternalServerErrorException, BadRequestException
from utils.general import get_ethereum_network_url, validate_conversion_with_blockchain, \
    get_cardano_network_url_and_project_id, check_existing_transaction_succeed, get_transactions_operation, \
    is_supported_network_conversion

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


def validate_cardano_address(address, chain_id):
    url, project_id = get_cardano_network_url_and_project_id(chain_id=chain_id)
    try:
        cardano_blockchain = CardanoBlockchainUtil(project_id=project_id, base_url=url)
        cardano_blockchain.get_address_detail(address=address)
    except Exception as e:
        if e.status_code == HTTPStatus.NOT_FOUND.value:
            pass
        elif e.status_code == HTTPStatus.BAD_REQUEST.value:
            raise BadRequestException(error_code=ErrorCode.INVALID_CARDANO_ADDRESS.value,
                                      error_details=ErrorDetails[ErrorCode.INVALID_CARDANO_ADDRESS.value].value)
        else:
            logger.exception(e)
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_CARDANO_ADDRESS_VALIDATION.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_CARDANO_ADDRESS_VALIDATION.value].value)


def validate_address(from_address, to_address, from_blockchain, to_blockchain):
    logger.info(f"validating the input address from_address={from_address}, from_blockchain={from_blockchain}"
                f", to_adress={to_address}, to_blockchain_name={to_blockchain}")
    from_blockchain_name = from_blockchain.get(BlockchainEntities.NAME.value)
    from_blockchain_chain_id = from_blockchain.get(BlockchainEntities.CHAIN_ID.value)

    to_blockchain_name = to_blockchain.get(BlockchainEntities.NAME.value)
    to_blockchain_chain_id = to_blockchain.get(BlockchainEntities.CHAIN_ID.value)

    if from_blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
        validate_cardano_address(address=from_address, chain_id=from_blockchain_chain_id)

    if to_blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
        validate_cardano_address(address=to_address, chain_id=to_blockchain_chain_id)


def get_lowest_unit_amount(amount, allowed_decimal):
    if allowed_decimal is None or allowed_decimal <= 0:
        return Decimal(amount)

    if allowed_decimal > MAX_ALLOWED_DECIMAL:
        raise InternalServerErrorException(error_code=ErrorCode.ALLOWED_DECIMAL_LIMIT_EXISTS.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.ALLOWED_DECIMAL_LIMIT_EXISTS.value].value)
    return Decimal(amount) * Decimal(math.pow(10, allowed_decimal))


def get_ethereum_transaction_details(chain_id, transaction_hash):
    network_url = get_ethereum_network_url(chain_id=chain_id)
    ethereum_web3_object = BlockChainUtil(provider_type="HTTP_PROVIDER", provider=network_url)
    try:
        blockchain_transaction = ethereum_web3_object.get_transaction_receipt_from_blockchain(
            transaction_hash=transaction_hash)
    except TransactionNotFound as e:
        raise BadRequestException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)
    except ValueError as e:
        raise BadRequestException(error_code=ErrorCode.RANDOM_TRANSACTION_HASH.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.RANDOM_TRANSACTION_HASH.value].value)
    except Exception as e:
        raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ETHEREUM_TRANSACTION_DETAILS.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNEXPECTED_ERROR_ETHEREUM_TRANSACTION_DETAILS.value].value)
    return blockchain_transaction


def validate_ethereum_transaction_details_against_conversion(chain_id, transaction_hash, conversion_on,
                                                             conversion_detail):
    blockchain_transaction = get_ethereum_transaction_details(chain_id=chain_id, transaction_hash=transaction_hash)

    if not validate_conversion_with_blockchain(conversion_on=conversion_on,
                                               address=blockchain_transaction.get("from"),
                                               amount=None, conversion_detail=conversion_detail):
        raise BadRequestException(error_code=ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value].value)


def get_cardano_transaction_details(chain_id, transaction_hash):
    url, project_id = get_cardano_network_url_and_project_id(chain_id=chain_id)
    try:
        cardano_blockchain = CardanoBlockchainUtil(project_id=project_id, base_url=url)
        blockchain_transaction = cardano_blockchain.get_transaction_utxos(transaction_hash=transaction_hash)
    except Exception as e:
        logger.info(repr(e))
        raise BadRequestException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)
    return blockchain_transaction


def validate_cardano_transaction_details_against_conversion(chain_id, transaction_hash, conversion_on,
                                                            conversion_detail):
    blockchain_transaction = get_cardano_transaction_details(chain_id=chain_id, transaction_hash=transaction_hash)
    if not validate_conversion_with_blockchain(conversion_on=conversion_on,
                                               address=blockchain_transaction.inputs[0].address,
                                               amount=None, conversion_detail=conversion_detail):
        raise BadRequestException(error_code=ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value].value)


def check_existing_transaction_state(transactions, conversion_on):
    if not check_existing_transaction_succeed(transactions):
        raise BadRequestException(error_code=ErrorCode.EXISTING_TRANSACTION_IS_NOT_SUCCEEDED.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.EXISTING_TRANSACTION_IS_NOT_SUCCEEDED.value].value)

    if len(transactions) and conversion_on == ConversionOn.TO.value:
        transactions_operation = get_transactions_operation(transactions=transactions)
        if TransactionOperation.TOKEN_CLAIMED.value in transactions_operation:
            raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_CREATED.value,
                                      error_details=ErrorDetails[
                                          ErrorCode.TRANSACTION_ALREADY_CREATED.value].value)


def validate_transaction_hash(conversion_detail, transaction_hash):
    transactions = conversion_detail.get(ConversionDetailEntities.TRANSACTIONS.value)

    from_blockchain = conversion_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {}).get(
        TokenEntities.BLOCKCHAIN.value, {})
    to_blockchain = conversion_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}).get(
        TokenEntities.BLOCKCHAIN.value, {})

    if not is_supported_network_conversion(from_blockchain=from_blockchain, to_blockchain=to_blockchain):
        logger.exception(
            f"Unsupported network conversion detected from_blockchain={from_blockchain}, to_blockchain={to_blockchain}")
        raise InternalServerErrorException(error_code=ErrorCode.UNSUPPORTED_CHAIN_ID.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNSUPPORTED_CHAIN_ID.value].value)

    if not len(transactions):
        conversion_on = ConversionOn.FROM.value
        blockchain = from_blockchain
    else:
        conversion_on = ConversionOn.TO.value
        blockchain = to_blockchain

    blockchain_name = blockchain.get(BlockchainEntities.NAME.value).lower()
    chain_id = blockchain.get(BlockchainEntities.CHAIN_ID.value)

    check_existing_transaction_state(transactions=transactions, conversion_on=conversion_on)

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
