import os
import time
from decimal import Decimal
from http import HTTPStatus
import re

from web3.logs import DISCARD
from web3.exceptions import TransactionNotFound, ABIFunctionNotFound

from pycardano import Address
from pycardano.exception import DecodingException

from application.service.cardano_service import CardanoService
from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from config import TOKEN_CONTRACT_PATH, MAX_RETRY, SLEEP_TIME
from constants.blockchain import CardanoTransactionEntities, CardanoBlockEntities, EthereumBlockchainEntities, \
    BinanceBlockchainEntities
from constants.entity import BlockchainEntities, TokenEntities, ConversionDetailEntities, TransactionEntities, \
    ConversionEntities, CardanoEventType, CardanoAPIEntities, WalletPairEntities, \
    EthereumAllowedEventType, CardanoAllowedEventType, CardanoServicesEventTypes, EthereumEventConsumerEntities, \
    BinanceAllowedEventType, BinanceEventConsumerEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, ConversionOn, MaxRetryEntities, SleepTimeEntities
from constants.status import TransactionOperation, EthereumToCardanoEvent, CardanoToEthereumEvent, TransactionStatus, \
    ConversionStatus, EthereumToBinanceEvent, BinanceToEthereumEvent, CardanoToCardanoEvent
from domain.entities.converter_bridge import ConverterBridge
from utils.cardano_blockchain import CardanoBlockchainUtil
from utils.exceptions import InternalServerErrorException, BadRequestException
from utils.general import get_ethereum_network_url, get_cardano_network_url_and_project_id, \
    check_existing_transaction_succeed, get_transactions_operation, get_binance_network_url, get_evm_network_url, \
    get_evm_blockchain
from utils.signature import validate_conversion_claim_signature
from infrastructure.repositories.blockchain_repository import BlockchainRepository

logger = get_logger(__name__)

blockchain_repo = BlockchainRepository()


def get_deposit_address_details(blockchain_name, token_name):
    logger.info(f"Getting the deposit address details for blockchain name={blockchain_name}, token_name={token_name}")
    deposit_address_details = {}
    if blockchain_name == BlockchainName.CARDANO.value:
        deposit_response = CardanoService.get_deposit_address(token_name=token_name)

        data = deposit_response.get(CardanoAPIEntities.DATA.value)
        if not data:
            raise InternalServerErrorException(
                error_code=ErrorCode.DATA_NOT_AVAILABLE_ON_DERIVED_ADDRESS.value,
                error_details=ErrorDetails[ErrorCode.DATA_NOT_AVAILABLE_ON_DERIVED_ADDRESS.value].value)

        derived_address = data.get(CardanoAPIEntities.DERIVED_ADDRESS.value)
        derived_address_index = data.get(CardanoAPIEntities.INDEX.value)
        derived_address_role = data.get(CardanoAPIEntities.ROLE.value)

        if not derived_address or derived_address_index is None or derived_address_role is None:
            raise InternalServerErrorException(
                error_code=ErrorCode.DERIVED_ADDRESS_NOT_FOUND.value,
                error_details=ErrorDetails[ErrorCode.DERIVED_ADDRESS_NOT_FOUND.value].value)

        deposit_address_details = get_deposit_address_details_format(derived_address=derived_address,
                                                                     index=derived_address_index,
                                                                     role=derived_address_role)

    return deposit_address_details


def get_deposit_address_details_format(derived_address, index, role):
    return {
        CardanoAPIEntities.DERIVED_ADDRESS.value: derived_address,
        CardanoAPIEntities.INDEX.value: index,
        CardanoAPIEntities.ROLE.value: role
    }


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
    logger.info(f"validating the input address from_address={from_address}, from_blockchain={from_blockchain}, "
                f"to_address={to_address}, to_blockchain_name={to_blockchain}")
    from_blockchain_name = from_blockchain.get(BlockchainEntities.NAME.value)
    from_blockchain_chain_id = from_blockchain.get(BlockchainEntities.CHAIN_ID.value)

    to_blockchain_name = to_blockchain.get(BlockchainEntities.NAME.value)
    to_blockchain_chain_id = to_blockchain.get(BlockchainEntities.CHAIN_ID.value)

    if from_blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
        validate_cardano_address(address=from_address, chain_id=from_blockchain_chain_id)

    if to_blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
        validate_cardano_address(address=to_address, chain_id=to_blockchain_chain_id)


def get_evm_transaction_details(web3_object, transaction_hash):
    try:
        blockchain_transaction = web3_object.get_transaction_receipt_from_blockchain(transaction_hash=transaction_hash)
    except TransactionNotFound as e:
        raise BadRequestException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                  error_details=ErrorDetails[ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)
    except ValueError as e:
        raise BadRequestException(error_code=ErrorCode.RANDOM_TRANSACTION_HASH.value,
                                  error_details=ErrorDetails[ErrorCode.RANDOM_TRANSACTION_HASH.value].value)
    except Exception as e:
        logger.exception(e)
        raise InternalServerErrorException(
            error_code=ErrorCode.UNEXPECTED_ERROR_ETHEREUM_TRANSACTION_DETAILS.value,
            error_details=ErrorDetails[ErrorCode.UNEXPECTED_ERROR_ETHEREUM_TRANSACTION_DETAILS.value].value)
    return blockchain_transaction


def get_event_logs(contract_instance, receipt, conversion_on):
    if conversion_on == ConversionOn.FROM.value:
        logs = contract_instance.events.ConversionOut().processReceipt(receipt, errors=DISCARD)
    else:
        logs = contract_instance.events.ConversionIn().processReceipt(receipt, errors=DISCARD)

    return logs


def get_converter_contract_balance(token_pair_id: str):
    logger.info(f"Get liquidity balance for token pair id {token_pair_id}")

    to_token_data = blockchain_repo.get_to_token_data_by_token_pair_id(token_pair_id)

    if not to_token_data:
        raise BadRequestException(error_code=ErrorCode.TOKEN_PAIR_NOT_EXISTS)

    blockchain_name, chain_id, token_symbol, contract_address = to_token_data

    if not blockchain_name or chain_id is None or not token_symbol:
        logger.error(f"Bad token data: blockchain_name={blockchain_name}, chain_id={chain_id}, "
                     f"token_symbol={token_symbol}, contract_address={contract_address}")
        raise InternalServerErrorException(error_code=ErrorCode.INVALID_TOKEN_DATA)

    if blockchain_name == BlockchainName.CARDANO.value:
        result = CardanoService.get_token_liquidity(token_name=token_symbol)
        result = result["data"]["balance"]
        return result
    elif blockchain_name in [BlockchainName.ETHEREUM.value, BlockchainName.BINANCE.value]:

        if not contract_address:
            logger.error(f"Bad contract address: contract_address={contract_address}")
            raise InternalServerErrorException(error_code=ErrorCode.INVALID_TOKEN_DATA)

        provider_url = get_evm_network_url(chain_id=chain_id)
        web3_object = BlockChainUtil(provider_type="HTTP_PROVIDER", provider=provider_url)
        contract_abi_path = get_token_contract_path(token=token_symbol)
        abi = web3_object.load_contract(path=contract_abi_path)
        contract_instance = web3_object.contract_instance(contract_abi=abi, address=contract_address)

        try:
            balance = contract_instance.functions.getConverterBalance().call()
            return balance
        except ABIFunctionNotFound as e:
            logger.error(f"Failed to get converter liquidity balance: {repr(e)}")
            raise BadRequestException(error_code=ErrorCode.NOT_LIQUID_CONTRACT)

    else:
        raise InternalServerErrorException(error_code=ErrorCode.UNSUPPORTED_CHAIN_ID)


def validate_evm_transaction_details_against_conversion(chain_id, transaction_hash, conversion_on,
                                                        contract_address, conversion_detail):
    blockchain_name = get_evm_blockchain(chain_id=chain_id)
    network_url = get_evm_network_url(chain_id=chain_id)
    evm_web3_object = BlockChainUtil(provider_type="HTTP_PROVIDER", provider=network_url)

    blockchain_transaction = get_evm_transaction_details(web3_object=evm_web3_object,
                                                         transaction_hash=transaction_hash)
    if conversion_on == ConversionOn.FROM.value:
        token_symbol = conversion_detail.get(ConversionDetailEntities.FROM_TOKEN.value).get(TokenEntities.SYMBOL.value)
    else:
        token_symbol = conversion_detail.get(ConversionDetailEntities.TO_TOKEN.value).get(TokenEntities.SYMBOL.value)

    contract_abi_path = get_token_contract_path(token=token_symbol)

    contract = evm_web3_object.load_contract(path=contract_abi_path)
    contract_instance = evm_web3_object.contract_instance(contract_abi=contract, address=contract_address)
    logs = get_event_logs(contract_instance=contract_instance, receipt=blockchain_transaction,
                          conversion_on=conversion_on)

    events = None
    if len(logs):
        if blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower():
            events = logs[0].get(EthereumEventConsumerEntities.ARGS.value)
        elif blockchain_name.lower() == BlockchainName.BINANCE.value.lower():
            events = logs[0].get(BinanceEventConsumerEntities.ARGS.value)

    if not len(logs) or not events:
        raise BadRequestException(error_code=ErrorCode.UNABLE_TO_FIND_EVENTS_FOR_HASH.value,
                                  error_details=ErrorDetails[ErrorCode.UNABLE_TO_FIND_EVENTS_FOR_HASH.value].value)

    if blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower():
        token_holder = events.get(EthereumEventConsumerEntities.TOKEN_HOLDER.value)
        amount = events.get(EthereumEventConsumerEntities.AMOUNT.value)
        conversion_id = events.get(EthereumEventConsumerEntities.CONVERSION_ID.value)
    elif blockchain_name.lower() == BlockchainName.BINANCE.value.lower():
        token_holder = events.get(BinanceEventConsumerEntities.TOKEN_HOLDER.value)
        amount = events.get(BinanceEventConsumerEntities.AMOUNT.value)
        conversion_id = events.get(BinanceEventConsumerEntities.CONVERSION_ID.value)
    else:
        token_holder = amount = conversion_id = None

    if not validate_conversion_with_blockchain(
            conversion_on=conversion_on,
            address=token_holder,
            amount=amount,
            conversion_id=conversion_id.decode("utf-8"),
            conversion_detail=conversion_detail,
            blockchain_name=blockchain_name):
        raise BadRequestException(
            error_code=ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value,
            error_details=ErrorDetails[ErrorCode.BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION.value].value)


def get_token_contract_path(token):
    token_contract_path = TOKEN_CONTRACT_PATH.get(token.lower())
    if not token_contract_path:
        raise InternalServerErrorException(
            error_code=ErrorCode.TOKEN_CONTRACT_ADDRESS_EMPTY.value,
            error_details=ErrorDetails[ErrorCode.TOKEN_CONTRACT_ADDRESS_EMPTY.value].value)

    return os.path.abspath(os.path.join(token_contract_path))


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
    logger.info(
        f"Validating the cardano transaction details for chain_id={chain_id},transaction_hash={transaction_hash}, "
        f"conversion_on={conversion_on}")
    blockchain_transaction = get_cardano_transaction_details(chain_id=chain_id, transaction_hash=transaction_hash)

    if blockchain_transaction is None or "error" in blockchain_transaction.to_dict():
        raise BadRequestException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND.value,
                                  error_details=ErrorDetails[ErrorCode.TRANSACTION_HASH_NOT_FOUND.value].value)


def check_existing_transaction_state(transactions, conversion_on):
    if not check_existing_transaction_succeed(transactions):
        raise BadRequestException(
            error_code=ErrorCode.EXISTING_TRANSACTION_IS_NOT_SUCCEEDED.value,
            error_details=ErrorDetails[ErrorCode.EXISTING_TRANSACTION_IS_NOT_SUCCEEDED.value].value)

    if len(transactions) and conversion_on == ConversionOn.TO.value:
        transactions_operation = get_transactions_operation(transactions=transactions)
        if TransactionOperation.TOKEN_MINTED.value in transactions_operation:
            raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_CREATED.value,
                                      error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_CREATED.value].value)


def get_next_activity_event_on_conversion(conversion_complete_detail):
    logger.info("Getting the next activity event on conversion")
    from_blockchain = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {})\
                                                .get(TokenEntities.BLOCKCHAIN.value, {}) \
                                                .get(BlockchainEntities.NAME.value).lower()
    to_blockchain = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}) \
                                              .get(TokenEntities.BLOCKCHAIN.value, {}) \
                                              .get(BlockchainEntities.NAME.value).lower()

    ethereum = BlockchainName.ETHEREUM.value.lower()
    cardano = BlockchainName.CARDANO.value.lower()
    binance = BlockchainName.BINANCE.value.lower()
    expected_events_flow = []

    if from_blockchain.lower() == ethereum and to_blockchain.lower() == cardano:
        expected_events_flow = EthereumToCardanoEvent
    elif from_blockchain.lower() == cardano and to_blockchain.lower() == ethereum:
        expected_events_flow = CardanoToEthereumEvent
    elif from_blockchain.lower() == ethereum and to_blockchain.lower() == binance:
        expected_events_flow = EthereumToBinanceEvent
    elif from_blockchain.lower() == binance and to_blockchain.lower() == ethereum:
        expected_events_flow = BinanceToEthereumEvent
    elif from_blockchain.lower() == cardano and to_blockchain.lower() == cardano:
        expected_events_flow = CardanoToCardanoEvent

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
                    raise InternalServerErrorException(
                        error_code=ErrorCode.TRANSACTION_WRONGLY_CREATED.value,
                        error_details=ErrorDetails[ErrorCode.TRANSACTION_WRONGLY_CREATED.value].value)
            else:
                next_event = expected_event
                break
            tx_list_index += 1

        if next_event:
            break
        conversion_side = ConversionOn.TO.value

    tx_amount = Decimal(conversion.get(ConversionEntities.DEPOSIT_AMOUNT.value))
    if conversion_side == ConversionOn.FROM.value:
        blockchain = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {}) \
                                               .get(TokenEntities.BLOCKCHAIN.value, {})
    elif conversion_side == ConversionOn.TO.value:
        blockchain = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}) \
                                               .get(TokenEntities.BLOCKCHAIN.value, {})
        tx_amount = Decimal(conversion.get(ConversionEntities.CLAIM_AMOUNT.value))
    else:
        blockchain = None

    if not next_event or not blockchain:
        logger.info("All conversions are done for this conversion")
    else:
        activity_event = ConverterBridge(blockchain_name=blockchain.get(BlockchainEntities.NAME.value),
                                         blockchain_network_id=blockchain.get(BlockchainEntities.CHAIN_ID.value),
                                         conversion_id=conversion.get(ConversionEntities.ID.value),
                                         tx_amount=tx_amount, tx_operation=next_event,
                                         conversion_side=conversion_side)

    return activity_event


def validate_tx_hash_presence_in_blockchain(blockchain_name, tx_hash, network_id):
    logger.info(f"Validating the transaction hash presence in blockchain for the blockchain_name={blockchain_name}, "
                f"tx_hash={tx_hash}, network_id={network_id}")
    try:
        if blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower():
            network_url = get_ethereum_network_url(chain_id=network_id)
            ethereum_web3_object = BlockChainUtil(provider_type="HTTP_PROVIDER", provider=network_url)
            transaction = ethereum_web3_object.get_transaction_receipt_from_blockchain(transaction_hash=tx_hash)
        elif blockchain_name.lower() == BlockchainName.BINANCE.value.lower():
            network_url = get_binance_network_url(chain_id=network_id)
            binance_web3_object = BlockChainUtil(provider_type="HTTP_PROVIDER", provider=network_url)
            transaction = binance_web3_object.get_transaction_receipt_from_blockchain(transaction_hash=tx_hash)
        else:
            url, project_id = get_cardano_network_url_and_project_id(chain_id=network_id)
            cardano_blockchain = CardanoBlockchainUtil(project_id=project_id, base_url=url)
            transaction = cardano_blockchain.get_transaction(hash=tx_hash)

        if not transaction:
            raise BadRequestException(error_code=ErrorCode.TRANSACTION_HASH_NOT_FOUND)

    except Exception as e:
        logger.error(f"Error occurred while checking for tx hash={tx_hash} presence in blockchain={blockchain_name}"
                     f" on the chain_id={network_id} because of {e}")
        raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_TX_HASH_PRESENCE)


def validate_consumer_event_type(blockchain_name, event_type):
    logger.info(f"Validating the consumer event type for blockchain_name={blockchain_name}, event_type={event_type}")
    if blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower() and event_type not in EthereumAllowedEventType:
        logger.info(f"Invalid event_type={event_type} provided, so skipping it")
        raise BadRequestException(error_code=ErrorCode.UNEXPECTED_EVENT_TYPE)
    elif blockchain_name.lower() == BlockchainName.BINANCE.value.lower() and event_type not in BinanceAllowedEventType:
        logger.info(f"Invalid event_type={event_type} provided, so skipping it")
        raise BadRequestException(error_code=ErrorCode.UNEXPECTED_EVENT_TYPE)
    elif blockchain_name.lower() == BlockchainName.CARDANO.value.lower() and event_type not in CardanoAllowedEventType:
        logger.info(f"Invalid event_type={event_type} provided, so skipping it ")
        raise BadRequestException(error_code=ErrorCode.UNEXPECTED_EVENT_TYPE)


def validate_consumer_event_against_transaction(event_type, transaction, blockchain_name):
    logger.info(f"Validating the consumer event against transaction for event_type={event_type}, "
                f"blockchain_name={blockchain_name}")

    if transaction and transaction.get(TransactionEntities.STATUS.value) == TransactionStatus.SUCCESS.value:
        raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_CONFIRMED.value,
                                  error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_CONFIRMED.value].value)

    if blockchain_name.lower() == BlockchainName.CARDANO.name.lower():
        if event_type in CardanoServicesEventTypes:
            if transaction is None:
                logger.info("Transaction is not available")
                raise BadRequestException(error_code=ErrorCode.TRANSACTION_NOT_FOUND)


def get_block_confirmation(tx_hash, blockchain_network_id):
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
    return bc_block_confirmations


def get_evm_block_confirmation(tx_hash, blockchain_network_id):
    blockchain_name = get_evm_blockchain(chain_id=blockchain_network_id)
    network_url = get_evm_network_url(chain_id=blockchain_network_id)
    evm_web3_object = BlockChainUtil(provider_type="HTTP_PROVIDER", provider=network_url)
    try:
        transaction = evm_web3_object.get_transaction_receipt_from_blockchain(transaction_hash=tx_hash)
        if blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower():
            bc_block_number = transaction.get(EthereumBlockchainEntities.BLOCK_NUMBER.value)
        elif blockchain_name.lower() == BlockchainName.BINANCE.value.lower():
            bc_block_number = transaction.get(BinanceBlockchainEntities.BLOCK_NUMBER.value)
        else:
            raise ValueError(f"EVM chain id {blockchain_network_id} is not supported")
        current_block_number = evm_web3_object.get_current_block_no()
        bc_block_confirmations = current_block_number - bc_block_number
    except Exception as e:
        raise InternalServerErrorException(
            error_code=ErrorCode.UNEXPECTED_ERROR_ON_BLOCK_CONFIRMATION.value,
            error_details=ErrorDetails[ErrorCode.UNEXPECTED_ERROR_ON_BLOCK_CONFIRMATION.value].value)
    return bc_block_confirmations


def generate_deposit_address_details_for_cardano_operation(wallet_pair):
    deposit_address = wallet_pair.get(WalletPairEntities.DEPOSIT_ADDRESS.value)
    deposit_address_details = wallet_pair.get(WalletPairEntities.DEPOSIT_ADDRESS_DETAIL.value)
    return {
        CardanoAPIEntities.ADDRESS.value: deposit_address,
        CardanoAPIEntities.INDEX.value: deposit_address_details.get(CardanoAPIEntities.INDEX.value),
        CardanoAPIEntities.ROLE.value: deposit_address_details.get(CardanoAPIEntities.ROLE.value)
    }


def validate_conversion_claim_request_signature(conversion_detail, amount, from_address, to_address, signature,
                                                chain_id):
    conversion = conversion_detail.get(ConversionDetailEntities.CONVERSION.value)
    conversion_id = conversion.get(ConversionEntities.ID.value)
    claim_amount = conversion.get(ConversionEntities.CLAIM_AMOUNT.value)
    claim_signature = conversion.get(ConversionEntities.CLAIM_SIGNATURE.value)
    conversion_status = conversion.get(ConversionEntities.STATUS.value)
    to_blockchain_name = conversion_detail.get(ConversionDetailEntities.TO_TOKEN.value) \
                                          .get(TokenEntities.BLOCKCHAIN.value) \
                                          .get(BlockchainEntities.NAME.value)

    if not claim_amount or not conversion_status or not to_blockchain_name or not conversion_id:
        raise BadRequestException(error_code=ErrorCode.CONVERSION_NOT_READY_FOR_CLAIM.value,
                                  error_details=ErrorDetails[ErrorCode.CONVERSION_NOT_READY_FOR_CLAIM.value].value)

    if to_blockchain_name.lower() not in [BlockchainName.ETHEREUM.value.lower(), BlockchainName.BINANCE.value.lower()]:
        raise BadRequestException(
            error_code=ErrorCode.INVALID_CLAIM_OPERATION_ON_BLOCKCHAIN.value,
            error_details=ErrorDetails[ErrorCode.INVALID_CLAIM_OPERATION_ON_BLOCKCHAIN.value].value)

    if conversion_status != ConversionStatus.WAITING_FOR_CLAIM.value:
        raise BadRequestException(error_code=ErrorCode.CONVERSION_NOT_READY_FOR_CLAIM.value,
                                  error_details=ErrorDetails[ErrorCode.CONVERSION_NOT_READY_FOR_CLAIM.value].value)

    result = validate_conversion_claim_signature(conversion_id=conversion_id, amount=amount,
                                                 from_address=from_address, to_address=to_address,
                                                 signature=signature, chain_id=chain_id)
    if result is False:
        raise BadRequestException(error_code=ErrorCode.INCORRECT_SIGNATURE.value,
                                  error_details=ErrorDetails[ErrorCode.INCORRECT_SIGNATURE.value].value)


def convert_str_to_decimal(value):
    return Decimal(value)


def convert_int_to_decimal(value):
    return Decimal(value)


def validate_conversion_request_amount(amount: str, min_value: str, max_value: str) -> None:
    logger.info(f"Validating the conversion request amount limits where amount={amount}, min_value={min_value}, "
                f"max_value={max_value}")
    min_value = Decimal(min_value)
    max_value = Decimal(max_value)
    amount = convert_str_to_decimal(value=amount)

    if (amount - int(amount)) > Decimal(0):
        raise BadRequestException(error_code=ErrorCode.INVALID_CONVERSION_AMOUNT_PROVIDED.value,
                                  error_details=ErrorDetails[
                                      ErrorCode.INVALID_CONVERSION_AMOUNT_PROVIDED.value].value)

    if not amount:
        raise BadRequestException(error_code=ErrorCode.CONVERSION_AMOUNT_CANT_BE_ZERO.value,
                                  error_details=ErrorDetails[ErrorCode.CONVERSION_AMOUNT_CANT_BE_ZERO.value].value)

    if amount < min_value:
        raise BadRequestException(error_code=ErrorCode.AMOUNT_LESS_THAN_MIN_VALUE.value,
                                  error_details=ErrorDetails[ErrorCode.AMOUNT_LESS_THAN_MIN_VALUE.value].value)

    if amount > max_value:
        raise BadRequestException(error_code=ErrorCode.AMOUNT_GREATER_THAN_MAX_VALUE.value,
                                  error_details=ErrorDetails[ErrorCode.AMOUNT_GREATER_THAN_MAX_VALUE.value].value)


def validate_conversion_with_blockchain(conversion_on, address, amount, conversion_id, conversion_detail,
                                        blockchain_name):
    logger.info(f"Validating the conversion with blockchain details conversion_on={conversion_on}, address={address}, "
                f"amount={amount}, blockchain_name={blockchain_name}")
    is_valid = True

    from_address = conversion_detail.get(ConversionDetailEntities.WALLET_PAIR.value, {}) \
                                    .get(WalletPairEntities.FROM_ADDRESS.value)
    to_address = conversion_detail.get(ConversionDetailEntities.WALLET_PAIR.value, {}) \
                                  .get(WalletPairEntities.TO_ADDRESS.value)
    deposit_amount = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {}) \
                                      .get(ConversionEntities.DEPOSIT_AMOUNT.value)
    claim_amount = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {}) \
                                    .get(ConversionEntities.CLAIM_AMOUNT.value)
    fee_amount = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {}) \
                                  .get(ConversionEntities.FEE_AMOUNT.value)
    conversion_claim_amount = convert_str_to_decimal(claim_amount) + convert_str_to_decimal(fee_amount)
    db_conversion_id = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {}) \
                                        .get(ConversionEntities.ID.value)

    if conversion_id != db_conversion_id:
        is_valid = False

    if conversion_on == ConversionOn.FROM.value and \
            (address != from_address or convert_int_to_decimal(amount) != convert_str_to_decimal(deposit_amount)):
        is_valid = False
    elif conversion_on == ConversionOn.TO.value and \
            (address != to_address or convert_int_to_decimal(amount) != conversion_claim_amount):
        is_valid = False

    return is_valid


def get_current_block_confirmation(blockchain_name, tx_hash, network_id):
    current_block_confirmation = 0
    logger.info("Getting the current block confirmation")
    i = 1
    BLOCK_CONFIRMATION_SLEEP_TIME = SLEEP_TIME.get(SleepTimeEntities.BLOCK_CONFIRMATION.value, 0)
    MAX_RETRY_BLOCK_CONFIRMATION = MAX_RETRY.get(MaxRetryEntities.BLOCK_CONFIRMATION.value, 0)

    while True:
        try:
            if blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
                current_block_confirmation = get_block_confirmation(tx_hash=tx_hash,
                                                                    blockchain_network_id=network_id)
            else:
                current_block_confirmation = get_evm_block_confirmation(tx_hash=tx_hash,
                                                                        blockchain_network_id=network_id)
        except Exception as e:
            logger.info(f"Transaction mayn't be available={e}, we will retry it ")

        if i > MAX_RETRY_BLOCK_CONFIRMATION:
            break

        if not current_block_confirmation:
            time.sleep(BLOCK_CONFIRMATION_SLEEP_TIME)
            logger.info(f"Waiting to get at least 1 block confirmation for the last "
                        f"{i * BLOCK_CONFIRMATION_SLEEP_TIME} seconds")
        else:
            break

        i += 1
    return current_block_confirmation


def wait_until_transaction_hash_exists_in_blockchain(tx_hash, network_id):
    logger.info("Waiting until the transaction hash exists in the blockchain exists ")
    i = 1
    SLEEP_TIME_TRANSACTION_HASH_PRESENCE = SLEEP_TIME.get(SleepTimeEntities.TRANSACTION_HASH_PRESENCE.value, 0)
    MAX_RETRY_TRANSACTION_HASH_PRESENCE = MAX_RETRY.get(MaxRetryEntities.TRANSACTION_HASH_PRESENCE.value, 0)

    url, project_id = get_cardano_network_url_and_project_id(chain_id=network_id)
    cardano_blockchain = CardanoBlockchainUtil(project_id=project_id, base_url=url)

    while True:
        transaction = None
        try:
            transaction = cardano_blockchain.get_transaction(hash=tx_hash)
        except Exception as e:
            logger.info(f"Transaction  hash mayn't be available={e}, we will retry it ")

        if i > MAX_RETRY_TRANSACTION_HASH_PRESENCE:
            break

        if not transaction:
            time.sleep(SLEEP_TIME_TRANSACTION_HASH_PRESENCE)
            logger.info(f"Waiting for transaction hash presence continues for last "
                        f"{i * SLEEP_TIME_TRANSACTION_HASH_PRESENCE} seconds")
        else:
            break

        i += 1


def is_valid_cardano_address(address: str) -> bool:
    if not re.match('^((Ae2)|(DdzFF)|(addr)).+$', address):
        return False
    if address.startswith("addr"):
        try:
            Address.decode(address)
        except DecodingException:
            return False
    return True
