import json
import math
from decimal import Decimal
from http import HTTPStatus

import requests
from web3.exceptions import TransactionNotFound

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from config import CARDANO_DEPOSIT_ADDRESS, CARDANO_SERVICE_API
from constants.blockchain import CardanoTransactionEntities, CardanoBlockEntities
from constants.entity import BlockchainEntities, TokenEntities, ConversionDetailEntities, TransactionEntities, \
    ConversionEntities, CardanoEventType, EthereumEventType, CardanoAPIEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, MAX_ALLOWED_DECIMAL, ConversionOn
from constants.status import TransactionOperation, EthereumToCardanoEvent, CardanoToEthereumEvent, TransactionStatus, \
    ConversionStatus
from domain.entities.converter_bridge import ConverterBridge
from utils.cardano_blockchain import CardanoBlockchainUtil
from utils.exceptions import InternalServerErrorException, BadRequestException, BlockConfirmationNotEnoughException
from utils.general import get_ethereum_network_url, validate_conversion_with_blockchain, \
    get_cardano_network_url_and_project_id, check_existing_transaction_succeed, get_transactions_operation, \
    is_supported_network_conversion
from utils.signature import validate_conversion_claim_signature

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
        if TransactionOperation.TOKEN_MINTED.value in transactions_operation:
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


def get_next_activity_event_on_conversion(conversion_complete_detail):
    logger.info("Getting the next activity event on conversion")
    from_blockchain = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {}).get(
        TokenEntities.BLOCKCHAIN.value, {}).get(BlockchainEntities.NAME.value).lower()
    to_blockchain = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}).get(
        TokenEntities.BLOCKCHAIN.value, {}).get(BlockchainEntities.NAME.value).lower()
    transactions = conversion_complete_detail.get(ConversionDetailEntities.TRANSACTIONS.value, [])

    if not len(transactions):
        logger.info("transactions can't be empty, expecting atleast one transaction should be success")
        raise BadRequestException(error_code=ErrorCode.NO_TRANSACTIONS_AVAILABLE.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.NO_TRANSACTIONS_AVAILABLE.value].value)

    expected_events_flow = []

    if from_blockchain.lower() == BlockchainName.ETHEREUM.value.lower() and to_blockchain.lower() == BlockchainName.CARDANO.value.lower():
        expected_events_flow = EthereumToCardanoEvent
    elif from_blockchain.lower() == BlockchainName.CARDANO.value.lower() and to_blockchain.lower() == BlockchainName.ETHEREUM.value.lower():
        expected_events_flow = CardanoToEthereumEvent

    return get_conversion_next_event(conversion_complete_detail=conversion_complete_detail,
                                     expected_events_flow=expected_events_flow)


def get_conversion_next_event(conversion_complete_detail, expected_events_flow):
    next_event = None
    activity_event = None
    tx_list_index = 0
    conversion = conversion_complete_detail.get(ConversionDetailEntities.CONVERSION.value, [])
    transactions = conversion_complete_detail.get(ConversionDetailEntities.TRANSACTIONS.value, [])

    conversion_side = ConversionOn.FROM.value
    for blockchain_name, expected_events in expected_events_flow.items():
        for expected_event in expected_events:
            if tx_list_index <= len(transactions) - 1:
                transaction = transactions[tx_list_index]
                if transaction.get(TransactionEntities.TRANSACTION_OPERATION.value) != expected_event:
                    raise InternalServerErrorException(error_code=ErrorCode.TRANSACTION_WRONGLY_CREATED.value,
                                                       error_details=ErrorDetails[
                                                           ErrorCode.TRANSACTION_WRONGLY_CREATED.value].value)
            else:
                next_event = expected_event
                break
            tx_list_index += 1

        if next_event:
            break
        conversion_side = ConversionOn.TO.value

    tx_amount = Decimal(float(conversion.get(ConversionEntities.DEPOSIT_AMOUNT.value)))
    if conversion_side == ConversionOn.FROM.value:
        blockchain = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {}).get(
            TokenEntities.BLOCKCHAIN.value, {})
    elif conversion_side == ConversionOn.TO.value:
        blockchain = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}).get(
            TokenEntities.BLOCKCHAIN.value, {})
        fee_amount = conversion.get(ConversionEntities.FEE_AMOUNT.value)
        if fee_amount:
            tx_amount = tx_amount - Decimal(float(fee_amount))
    else:
        blockchain = None

    if not next_event or not blockchain:
        logger.info("All conversions are done for this conversion")
    else:
        conversion_bridge_obj = ConverterBridge(blockchain_name=blockchain.get(BlockchainEntities.NAME.value),
                                                blockchain_network_id=blockchain.get(BlockchainEntities.CHAIN_ID.value),
                                                conversion_id=conversion.get(ConversionEntities.ID.value),
                                                tx_amount=tx_amount, tx_operation=next_event)
        activity_event = conversion_bridge_obj.to_dict()

    return activity_event


def validate_consumer_event_against_transaction(event_type, transaction, blockchain_name):
    logger.info("Validating the consumer event")
    if blockchain_name.lower() == BlockchainName.CARDANO.name.lower():
        if event_type == CardanoEventType.TOKEN_RECEIVED.value and transaction:
            logger.info("transaction already updated")
            raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_PROCESSED.value,
                                      error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_PROCESSED.value].value)
        elif event_type == CardanoEventType.TOKEN_MINTED.value or event_type == CardanoEventType.TOKEN_BURNT.value:
            if transaction is None:
                logger.info("Transaction is not available")
                raise BadRequestException(error_code=ErrorCode.TRANSACTION_NOT_FOUND.value,
                                          error_details=ErrorDetails[ErrorCode.TRANSACTION_NOT_FOUND.value].value)

            if transaction.get(TransactionEntities.STATUS.value) == TransactionStatus.SUCCESS.value:
                logger.info("Transaction already confirmed")
                raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_CONFIRMED.value,
                                          error_details=ErrorDetails[
                                              ErrorCode.TRANSACTION_ALREADY_CONFIRMED.value].value)
    elif blockchain_name.lower() == BlockchainName.ETHEREUM.name.lower():
        if (event_type == EthereumEventType.TOKEN_BURNT.value or event_type == EthereumEventType.TOKEN_MINTED.value) and \
                transaction and transaction.get(TransactionEntities.STATUS.value) == TransactionStatus.SUCCESS.value:
            logger.info("Transaction already confirmed")
            raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_CONFIRMED.value,
                                      error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_CONFIRMED.value].value)


def check_block_confirmation(tx_hash, blockchain_network_id, required_block_confirmation):
    url, project_id = get_cardano_network_url_and_project_id(chain_id=blockchain_network_id)
    cardano_blockchain = CardanoBlockchainUtil(project_id=project_id, base_url=url)
    try:
        transaction = cardano_blockchain.get_transaction(hash=tx_hash)
        bc_block_height = transaction.get(CardanoTransactionEntities.BLOCK_HEIGHT.value)
        block_details = cardano_blockchain.get_block(hash_or_number=bc_block_height)

        bc_block_confirmations = block_details.get(CardanoBlockEntities.CONFIRMATIONS.value)

    except Exception as e:
        raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_BLOCK_CONFIRMATION.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNEXPECTED_ERROR_ON_BLOCK_CONFIRMATION.value].value)

    if bc_block_confirmations < required_block_confirmation:
        raise BlockConfirmationNotEnoughException(error_code=ErrorCode.NOT_ENOUGH_BLOCK_CONFIRMATIONS.value,
                                                  error_details=ErrorDetails[
                                                      ErrorCode.NOT_ENOUGH_BLOCK_CONFIRMATIONS.value].value)


def burn_token_on_cardano(address, token, tx_amount, tx_details):
    logger.info(
        f"Calling the burn token service on cardano with inputs as address={address}, {token}, tx_amount={tx_amount}, "
        f"tx_details={tx_details}")

    base_path = CARDANO_SERVICE_API['CARDANO_SERVICE_BASE_PATH']
    if not base_path:
        raise InternalServerErrorException(error_code=ErrorCode.LAMBDA_ARN_BURN_NOT_FOUND.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.LAMBDA_ARN_BURN_NOT_FOUND.value].value)
    try:
        payload = generate_payload_format_for_cardano_operation(address=address,
                                                                tx_amount=str(Decimal(float(tx_amount))),
                                                                tx_details=tx_details)
        logger.info(f"Payload for burning ={json.dumps(payload)}")
        response = requests.post(f"{base_path}/{token}/burn", data=json.dumps(payload),
                                 headers={"Content-Type": "application/json"})

        if response.status_code != HTTPStatus.OK.value:
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)
        response = json.loads(response.content.decode("utf-8"))

    except Exception as e:
        logger.exception(f"Unexpected error while calling the cardano burn service={e}")
        raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)

    if not response.get(CardanoAPIEntities.TRANSACTION_ID.value):
        raise InternalServerErrorException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)

    return response


def mint_token_and_transfer_on_cardano(address, token, tx_amount, tx_details, source_address):
    logger.info(
        f"Calling the mint token service on cardano with inputs as address={address}, token={token}, tx_amount={tx_amount}, tx_details={tx_details}, source_address={source_address}")

    base_path = CARDANO_SERVICE_API['CARDANO_SERVICE_BASE_PATH']
    if not base_path:
        raise InternalServerErrorException(error_code=ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value].value)

    try:
        payload = generate_payload_format_for_cardano_operation(address=address,
                                                                tx_amount=str(Decimal(float(tx_amount))),
                                                                tx_details=tx_details)
        payload[CardanoAPIEntities.SOURCE_ADDRESS.value] = source_address
        logger.info(f"Payload for minting = {json.dumps(payload)}")

        response = requests.post(f"{base_path}/{token}/mint", data=json.dumps(payload),
                                 headers={"Content-Type": "application/json"})

        if response.status_code != HTTPStatus.OK.value:
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)

        response = json.loads(response.content.decode("utf-8"))
    except Exception as e:
        logger.exception(f"Unexpected error while calling the cardano mint service={e}")
        raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)

    if not response.get(CardanoAPIEntities.TRANSACTION_ID.value):
        raise InternalServerErrorException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)

    return response


def generate_transaction_detail_for_cardano_operation(hash, environment):
    return {
        CardanoAPIEntities.HASH.value: hash,
        CardanoAPIEntities.ENVIRONMENT.value: environment
    }


def generate_payload_format_for_cardano_operation(address, tx_amount, tx_details):
    return {
        CardanoAPIEntities.CARDANO_ADDRESS.value: address, CardanoAPIEntities.AMOUNT.value: tx_amount,
        CardanoAPIEntities.TRANSACTION_DETAILS.value: tx_details
    }


def validate_conversion_claim_request_signature(conversion_detail, amount, from_address, to_address, signature,
                                                chain_id):
    conversion = conversion_detail.get(ConversionDetailEntities.CONVERSION.value)
    conversion_id = conversion.get(ConversionEntities.ID.value)
    claim_amount = conversion.get(ConversionEntities.CLAIM_AMOUNT.value)
    claim_signature = conversion.get(ConversionEntities.CLAIM_SIGNATURE.value)
    conversion_status = conversion.get(ConversionEntities.STATUS.value)
    to_blockchain_name = conversion_detail.get(ConversionDetailEntities.TO_TOKEN.value).get(
        TokenEntities.BLOCKCHAIN.value).get(BlockchainEntities.NAME.value)

    if not claim_amount or not conversion_status or not to_blockchain_name or not conversion_id:
        raise BadRequestException(error_code=ErrorCode.CONVERSION_NOT_READY_FOR_CLAIM.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.CONVERSION_NOT_READY_FOR_CLAIM.value].value)

    if to_blockchain_name.lower() != BlockchainName.ETHEREUM.value.lower():
        raise BadRequestException(error_code=ErrorCode.INVALID_CLAIM_OPERATION_ON_BLOCKCHAIN.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.INVALID_CLAIM_OPERATION_ON_BLOCKCHAIN.value].value)

    if claim_signature:
        raise BadRequestException(error_code=ErrorCode.CONVERSION_ALREADY_CLAIMED.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.CONVERSION_ALREADY_CLAIMED.value].value)

    if conversion_status != ConversionStatus.WAITING_FOR_CLAIM.value:
        raise BadRequestException(error_code=ErrorCode.CONVERSION_NOT_READY_FOR_CLAIM.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.CONVERSION_NOT_READY_FOR_CLAIM.value].value)

    result = validate_conversion_claim_signature(conversion_id=conversion_id, amount=amount,
                                                 from_address=from_address, to_address=to_address,
                                                 signature=signature, chain_id=chain_id)
    if result is False:
        raise BadRequestException(error_code=ErrorCode.INCORRECT_SIGNATURE.value,
                                  error_details=ErrorDetails[ErrorCode.INCORRECT_SIGNATURE.value].value)
