import ast
import json
from decimal import Decimal

from application.service.blockchain_service import BlockchainService
from application.service.conversion_service import ConversionService
from application.service.notification_service import NotificationService
from application.service.wallet_pair_service import WalletPairService
from common.logger import get_logger
from constants.entity import CardanoEventType, BlockchainEntities, CardanoEventConsumer, EventConsumerEntity, \
    WalletPairEntities, ConversionEntities, ConverterBridgeEntities, EthereumEventConsumerEntities, EthereumEventType, \
    TransactionEntities, TokenEntities, ConversionDetailEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, CreatedBy, QueueName
from constants.status import TransactionStatus, TransactionVisibility, TransactionOperation, \
    ALLOWED_CONVERTER_BRIDGE_TX_OPERATIONS, ConversionStatus, ConversionTransactionStatus
from utils.blockchain import get_next_activity_event_on_conversion, validate_consumer_event_against_transaction, \
    check_block_confirmation, burn_token_on_cardano, mint_token_and_transfer_on_cardano
from utils.exceptions import BadRequestException, InternalServerErrorException

logger = get_logger(__name__)


class ConsumerService:

    def __init__(self):
        self.blockchain_service = BlockchainService()
        self.conversion_service = ConversionService()
        self.wallet_pair_service = WalletPairService()

    def converter_event_consumer(self, payload):
        blockchain_name = payload.get(EventConsumerEntity.BLOCKCHAIN_NAME.value)
        blockchain_event = payload.get(EventConsumerEntity.BLOCKCHAIN_EVENT.value)

        if not blockchain_name or not blockchain_event:
            logger.info(
                f"Either blockchain name={blockchain_name} or blockchain_event={blockchain_event}  is empty")
            raise BadRequestException(error_code=ErrorCode.CONSUMER_EVENT_EMPTY.value,
                                      error_details=ErrorDetails[ErrorCode.CONSUMER_EVENT_EMPTY.value].value)

        blockchain_detail = self.blockchain_service.get_blockchain(blockchain_name=blockchain_name)

        if not blockchain_detail:
            logger.info("Not supported blockchain")
            raise BadRequestException(error_code=ErrorCode.UNSUPPORTED_BLOCKCHAIN_ON_SYSTEM.value,
                                      error_details=ErrorDetails[
                                          ErrorCode.UNSUPPORTED_BLOCKCHAIN_ON_SYSTEM.value].value)

        if blockchain_name.lower() == BlockchainName.ETHEREUM.name.lower():
            event_type = blockchain_event.get(EthereumEventConsumerEntities.NAME.value)
            tx_hash = blockchain_event.get(EthereumEventConsumerEntities.DATA.value, {}).get(
                EthereumEventConsumerEntities.TRANSACTION_HASH.value)
            blockchain_network_id = blockchain_detail.get(BlockchainEntities.CHAIN_ID.value)
        elif blockchain_name.lower() == BlockchainName.CARDANO.name.lower():
            event_type = blockchain_event.get(CardanoEventConsumer.TRANSACTION_DETAIL.value, {}).get(
                CardanoEventConsumer.TX_TYPE.value)
            tx_hash = blockchain_event.get(CardanoEventConsumer.TX_HASH.value)
            blockchain_network_id = blockchain_detail.get(BlockchainEntities.CHAIN_ID.value)
        else:
            raise BadRequestException(error_code=ErrorCode.UNHANDLED_BLOCKCHAIN_OPERATION.value,
                                      error_details=ErrorDetails[ErrorCode.UNHANDLED_BLOCKCHAIN_OPERATION.value].value)

        if not event_type or not tx_hash or not blockchain_network_id or not blockchain_event or not blockchain_detail:
            raise BadRequestException(error_code=ErrorCode.CONSUMER_EVENT_EMPTY.value,
                                      error_details=ErrorDetails[ErrorCode.CONSUMER_EVENT_EMPTY.value].value)

        self.process_event_consumer(event_type=event_type, tx_hash=tx_hash, network_id=blockchain_network_id,
                                    blockchain_event=blockchain_event, blockchain_detail=blockchain_detail)

    def process_event_consumer(self, event_type, tx_hash, network_id, blockchain_event, blockchain_detail):
        blockchain_name = blockchain_detail.get(BlockchainEntities.NAME.value)

        # validate block confirmations for cardano side
        if blockchain_name.lower() == BlockchainName.CARDANO.name.lower():
            blockchain_confirmation = blockchain_event.get(CardanoEventConsumer.TRANSACTION_DETAIL.value, {}).get(
                CardanoEventConsumer.CONFIRMATIONS.value)
            required_block_confirmation = blockchain_detail.get(BlockchainEntities.BLOCK_CONFIRMATION.value)

            if blockchain_confirmation is None:
                blockchain_confirmation = 0

            if required_block_confirmation and required_block_confirmation > blockchain_confirmation:
                check_block_confirmation(tx_hash=tx_hash, blockchain_network_id=network_id,
                                         required_block_confirmation=required_block_confirmation)

        transaction = self.conversion_service.get_transaction_by_hash(tx_hash=tx_hash)

        validate_consumer_event_against_transaction(event_type=event_type, transaction=transaction)

        if event_type == EthereumEventType.LOCK_TOKEN.value or event_type == EthereumEventType.UNLOCK_TOKEN.value:
            json_str = blockchain_event.get(EthereumEventConsumerEntities.DATA.value, {}).get(
                EthereumEventConsumerEntities.JSON_STR.value)
            metadata = ast.literal_eval(json_str)

            if event_type == EthereumEventType.LOCK_TOKEN.value:
                tx_amount = metadata.get(EthereumEventConsumerEntities.LOCK_AMOUNT.value)
            else:
                tx_amount = metadata.get(EthereumEventConsumerEntities.UNLOCK_AMOUNT.value)

            conversion = self.process_ethereum_event(event_type=event_type, tx_hash=tx_hash, tx_amount=tx_amount,
                                                     conversion_id=metadata.get(
                                                         EthereumEventConsumerEntities.CONVERSION_ID.value),
                                                     transaction=transaction, token_holder=metadata.get(
                    EthereumEventConsumerEntities.TOKEN_HOLDER.value))
        elif event_type == CardanoEventType.TOKEN_RECEIVED.value:
            conversion = self.process_cardano_token_received_event(blockchain_event=blockchain_event)
        elif event_type == CardanoEventType.TOKEN_MINTED.value:
            conversion = self.process_cardano_token_mint_event(tx_id=transaction.get(TransactionEntities.ID.value))
        elif event_type == CardanoEventType.TOKEN_BURNT.value:
            conversion = self.process_cardano_token_burnt_event(tx_id=transaction.get(TransactionEntities.ID.value))
        else:
            logger.info(f"Invalid event type provided ={event_type}")
            raise BadRequestException(error_code=ErrorCode.UNEXPECTED_EVENT_TYPE.value,
                                      error_details=ErrorDetails[ErrorCode.UNEXPECTED_EVENT_TYPE.value].value)

        conversion_complete_detail = self.conversion_service.get_conversion_complete_detail(
            conversion_id=conversion.get(ConversionEntities.ID.value))

        if not conversion_complete_detail:
            logger.info("Invalid conversion id provided")
            raise BadRequestException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                      error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        activity_event = get_next_activity_event_on_conversion(conversion_complete_detail=conversion_complete_detail)

        if activity_event:
            NotificationService.send_message_to_queue(queue=QueueName.CONVERTER_BRIDGE.value,
                                                      message=json.dumps(activity_event))
        else:
            conversion_transaction_id = conversion_complete_detail.get(ConversionDetailEntities.TRANSACTIONS.value,
                                                                       {}).get(
                TransactionEntities.CONVERSION_TRANSACTION_ID.value)
            self.conversion_service.update_conversion_transaction(conversion_transaction_id=conversion_transaction_id,
                                                                  status=ConversionTransactionStatus.SUCCESS.value)
            self.conversion_service.update_conversion(conversion_id=conversion.get(ConversionEntities.ID.value),
                                                      status=ConversionStatus.SUCCESS.value)
            logger.info("Conversion is done")

    def process_ethereum_event(self, event_type, tx_hash, tx_amount, conversion_id, transaction, token_holder):

        if not tx_hash or not tx_amount or not conversion_id:
            raise BadRequestException(error_code=ErrorCode.MISSING_ETHEREUM_EVENT_FIELDS.value,
                                      error_details=ErrorDetails[ErrorCode.MISSING_ETHEREUM_EVENT_FIELDS.value].value)

        conversion = self.conversion_service.get_conversion_detail(conversion_id=conversion_id)

        if not conversion:
            raise BadRequestException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                      error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        wallet_pair = self.wallet_pair_service.get_wallet_pair_by_conversion_id(conversion_id=conversion_id)

        if event_type == EthereumEventType.LOCK_TOKEN.value and (conversion.get(
                ConversionEntities.DEPOSIT_AMOUNT.value) != tx_amount or wallet_pair.get(
            WalletPairEntities.FROM_ADDRESS.value) == token_holder):
            logger.info("Mismatch on address and amount from request and contract for lock event")
            raise BadRequestException(error_code=ErrorCode.MISMATCH_AMOUNT.value,
                                      error_details=ErrorDetails[ErrorCode.MISMATCH_AMOUNT.value].value)
        elif event_type == EthereumEventType.UNLOCK_TOKEN.value and (
                conversion.get(ConversionEntities.CLAIM_AMOUNT.value) != tx_amount or wallet_pair.get(
            WalletPairEntities.TO_ADDRESS.value) == token_holder):
            logger.info("Mismatch on address and amount from request and contract for unlock event")
            raise BadRequestException(error_code=ErrorCode.MISMATCH_AMOUNT.value,
                                      error_details=ErrorDetails[ErrorCode.MISMATCH_AMOUNT.value].value)

        if not transaction:
            transaction = self.conversion_service.create_transaction_for_conversion(conversion_id=conversion_id,
                                                                                    transaction_hash=tx_hash)

        if transaction.get(TransactionEntities.STATUS.value) == TransactionStatus.SUCCESS.value:
            raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_PROCESSED.value,
                                      error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_PROCESSED.value].value)

        self.conversion_service.update_transaction_by_id(tx_id=transaction.get(TransactionEntities.ID.value),
                                                         tx_operation=TransactionOperation.TOKEN_RECEIVED.value,
                                                         tx_visibility=TransactionVisibility.EXTERNAL.value,
                                                         tx_amount=tx_amount,
                                                         tx_status=TransactionStatus.SUCCESS.value)
        return conversion

    def process_cardano_token_received_event(self, blockchain_event):
        tx_hash = blockchain_event.get(CardanoEventConsumer.TX_HASH.value)
        deposit_address = blockchain_event.get(CardanoEventConsumer.ADDRESS.value)
        tx_amount = blockchain_event.get(CardanoEventConsumer.TRANSACTION_DETAIL.value, {}).get(
            CardanoEventConsumer.TX_AMOUNT.value)

        if deposit_address is None or tx_amount is None or tx_hash is None:
            raise BadRequestException(error_code=ErrorCode.MISSING_CARDANO_EVENT_FIELDS.value,
                                      error_details=ErrorDetails[ErrorCode.MISSING_CARDANO_EVENT_FIELDS.value].value)

        tx_amount = Decimal(float(tx_amount))
        created_by = None

        conversion = self.conversion_service.get_waiting_conversion_deposit_on_address(deposit_address=deposit_address)
        try:
            if conversion is None:
                wallet_pair = self.wallet_pair_service.get_wallet_pair_by_deposit_address(
                    deposit_address=deposit_address)
                if wallet_pair is None:
                    logger.info("Wallet pair doesn't exist")
                    raise BadRequestException(error_code=ErrorCode.WALLET_PAIR_NOT_EXISTS.value,
                                              error_details=ErrorDetails[ErrorCode.WALLET_PAIR_NOT_EXISTS.value].value)

                created_by = CreatedBy.BACKEND.value
                conversion = self.conversion_service.create_conversion(
                    wallet_pair_id=wallet_pair.get(WalletPairEntities.ROW_ID.value), deposit_amount=tx_amount,
                    created_by=created_by)
            else:
                created_by = CreatedBy.DAPP.value

            transaction = self.conversion_service.create_transaction_for_conversion(
                conversion_id=conversion.get(ConversionEntities.ID.value),
                transaction_hash=tx_hash, created_by=created_by)

            self.conversion_service.update_transaction_by_id(tx_id=transaction.get(TransactionEntities.ID.value),
                                                             tx_operation=TransactionOperation.TOKEN_RECEIVED.value,
                                                             tx_visibility=TransactionVisibility.EXTERNAL.value,
                                                             tx_amount=tx_amount,
                                                             tx_status=TransactionStatus.SUCCESS.value,
                                                             created_by=created_by)
        except BadRequestException as e:
            logger.info(f"Bad Request {e}")
            raise BadRequestException(error_code=ErrorCode.BAD_REQUEST_ON_TRANSACTION_CREATION.value,
                                      error_details=ErrorDetails[
                                          ErrorCode.BAD_REQUEST_ON_TRANSACTION_CREATION.value].value)
        except Exception as e:
            logger.exception(f"Unexpected error occurred while creating the transaction={e} ")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_TRANSACTION_CREATION.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_TRANSACTION_CREATION.value].value)

        if tx_amount != Decimal(float(conversion.get(ConversionEntities.DEPOSIT_AMOUNT.value))):
            self.conversion_service.update_conversion_amount(conversion_id=conversion.get(ConversionEntities.ID.value),
                                                             deposit_amount=tx_amount)

        return conversion

    def converter_bridge(self, payload):
        blockchain_name = payload.get(ConverterBridgeEntities.BLOCKCHAIN_NAME.value)
        blockchain_event = payload.get(ConverterBridgeEntities.BLOCKCHAIN_EVENT.value, {})

        conversion_id = blockchain_event.get(ConverterBridgeEntities.CONVERSION_ID.value)
        tx_amount = blockchain_event.get(ConverterBridgeEntities.TX_AMOUNT.value)
        tx_operation = blockchain_event.get(ConverterBridgeEntities.TX_OPERATION.value)

        if not blockchain_name or not conversion_id or not tx_amount or not tx_operation \
                or tx_operation not in ALLOWED_CONVERTER_BRIDGE_TX_OPERATIONS:
            logger.info(
                f"Required field(s) blockchain_name={blockchain_name}, conversion_id={conversion_id}, tx_amount={tx_amount}, "
                f"tx_operation={tx_operation} are missing or invalid values provided")
            raise BadRequestException(error_code=ErrorCode.MISSING_CONVERTER_BRIDGE_FIELDS.value,
                                      error_details=ErrorDetails[ErrorCode.MISSING_CONVERTER_BRIDGE_FIELDS.value].value)

        conversion_complete_detail = self.conversion_service.get_conversion_complete_detail(conversion_id=conversion_id)
        if not conversion_complete_detail:
            logger.info(f"Invalid conversion_id={conversion_id} provided")
            raise BadRequestException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                      error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        activity_event = get_next_activity_event_on_conversion(conversion_complete_detail=conversion_complete_detail)

        if payload == activity_event:
            self.process_converter_bridge_request(
                conversion_complete_detail=conversion_complete_detail, payload=payload)
            print("Successfully processed the request")
        else:
            logger.info("Unable to match the request activity event")
            raise BadRequestException(error_code=ErrorCode.ACTIVITY_EVENT_NOT_MATCHING.value,
                                      error_details=ErrorDetails[ErrorCode.ACTIVITY_EVENT_NOT_MATCHING.value].value)

    def process_cardano_token_burnt_event(self, tx_id):
        self.conversion_service.update_transaction_by_id(tx_id=tx_id, tx_status=TransactionStatus.SUCCESS.value)
        return self.conversion_service.get_conversion_detail_by_tx_id(tx_id=tx_id)

    def process_cardano_token_mint_event(self, tx_id):
        self.conversion_service.update_transaction_by_id(tx_id=tx_id, tx_status=TransactionStatus.SUCCESS.value)
        return self.conversion_service.get_conversion_detail_by_tx_id(tx_id=tx_id)

    def process_ethereum_unlock_token_event(self, tx_id):
        self.conversion_service.update_transaction_by_id(tx_id=tx_id, tx_status=TransactionStatus.SUCCESS.value)
        return self.conversion_service.get_conversion_detail_by_tx_id(tx_id=tx_id)

    def process_converter_bridge_request(self, conversion_complete_detail, payload):
        from_blockchain = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {}).get(
            TokenEntities.BLOCKCHAIN.value, {}).get(BlockchainEntities.NAME.value).lower()
        to_blockchain = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}).get(
            TokenEntities.BLOCKCHAIN.value, {}).get(BlockchainEntities.NAME.value).lower()
        transactions = conversion_complete_detail.get(ConversionDetailEntities.TRANSACTIONS.value, [])

        target_token = {}
        if from_blockchain.lower() == payload.get(ConverterBridgeEntities.BLOCKCHAIN_NAME.value).lower():
            target_token = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {})
        elif to_blockchain.lower() == payload.get(ConverterBridgeEntities.BLOCKCHAIN_NAME.value).lower():
            target_token = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {})

        blockchain_event = payload.get(ConverterBridgeEntities.BLOCKCHAIN_EVENT.value)
        tx_amount = blockchain_event.get(ConverterBridgeEntities.TX_AMOUNT.value)
        tx_operation = blockchain_event.get(ConverterBridgeEntities.TX_OPERATION.value)

        tx_hash = None
        if tx_operation == TransactionOperation.TOKEN_BURNT.value:
            tx_hash = burn_token_on_cardano(token=target_token.get(TokenEntities.SYMBOL.value), tx_amount=tx_amount,
                                            tx_details={})
        elif tx_operation == TransactionOperation.TOKEN_MINT_AND_TRANSFER.value:
            tx_hash = mint_token_and_transfer_on_cardano(token=target_token.get(TokenEntities.SYMBOL.value),
                                                         tx_amount=tx_amount, tx_details={})
        elif tx_operation == TransactionOperation.TOKEN_UNLOCKED.value:
            self.conversion_service.update_conversion(
                conversion_id=conversion_complete_detail.get(ConversionDetailEntities.CONVERSION.value, {}).get(
                    ConversionEntities.ID.value),
                claim_amount=tx_amount, status=ConversionStatus.WAITING_FOR_CLAIM.value)
        else:
            logger.info("Invalid tx_operation provided")
            raise BadRequestException(error_code=ErrorCode.INVALID_TRANSACTION_OPERATION_PROVIDED.value,
                                      error_details=ErrorDetails[
                                          ErrorCode.INVALID_TRANSACTION_OPERATION_PROVIDED.value].value)

        if tx_operation != TransactionOperation.TOKEN_UNLOCKED.value:
            self.conversion_service.create_transaction(
                conversion_transaction_id=transactions[0].get(TransactionEntities.CONVERSION_TRANSACTION_ID.value),
                from_token_id=target_token.get(TokenEntities.ROW_ID.value),
                to_token_id=target_token.get(TokenEntities.ROW_ID.value),
                transaction_visibility=TransactionVisibility.EXTERNAL.value,
                transaction_operation=tx_operation, transaction_hash=tx_hash,
                transaction_amount=tx_amount,
                status=TransactionStatus.WAITING_FOR_CONFIRMATION.value,
                created_by=CreatedBy.BACKEND.value)
