import ast
import json
from decimal import Decimal

from application.service.blockchain_service import BlockchainService
from application.service.cardano_service import CardanoService
from application.service.conversion_service import ConversionService
from application.service.notification_service import NotificationService
from application.service.pooling_service import PoolingService
from application.service.token_service import TokenService
from application.service.wallet_pair_service import WalletPairService
from common.logger import get_logger
from config import MESSAGE_GROUP_ID, SLACK_HOOK
from constants.entity import CardanoEventType, BlockchainEntities, CardanoEventConsumer, EventConsumerEntity, \
    WalletPairEntities, ConversionEntities, ConverterBridgeEntities, EthereumEventConsumerEntities, EthereumEventType, \
    TransactionEntities, TokenEntities, ConversionDetailEntities, CardanoAPIEntities, TokenPairEntities, \
    ConversionFeeEntities, MessagePoolEntities, BinanceEventConsumerEntities, BinanceEventType
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, CreatedBy, QueueName
from constants.status import TransactionStatus, TransactionVisibility, TransactionOperation, \
    ALLOWED_CONVERTER_BRIDGE_TX_OPERATIONS, ConversionStatus, ConversionTransactionStatus
from utils.general import update_decimal_places, reset_decimal_places
from utils.blockchain import get_next_activity_event_on_conversion, validate_consumer_event_against_transaction, \
    generate_deposit_address_details_for_cardano_operation, calculate_fee_amount, \
    validate_conversion_request_amount, validate_consumer_event_type, convert_str_to_decimal, \
    get_current_block_confirmation, wait_until_transaction_hash_exists_in_blockchain, \
    validate_tx_hash_presence_in_blockchain
from utils.exception_handler import bridge_exception_handler
from utils.exceptions import BadRequestException, InternalServerErrorException, BlockConfirmationNotEnoughException

logger = get_logger(__name__)


class ConsumerService:

    def __init__(self):
        self.blockchain_service = BlockchainService()
        self.conversion_service = ConversionService()
        self.wallet_pair_service = WalletPairService()
        self.token_service = TokenService()
        self.pool_service = PoolingService()

    @staticmethod
    def post_converter_ethereum_events_to_queue(payload):
        logger.info(f"Posting the ethereum event to queue of payload={payload}")
        NotificationService.send_message_to_queue(queue=QueueName.EVENT_CONSUMER.value, message=json.dumps(payload),
                                                  message_group_id=None)
        logger.info("Finished posting message to queue")

    def converter_event_consumer(self, payload):
        logger.info(f"Converter event consumer received the payload={payload}")
        blockchain_name = payload.get(EventConsumerEntity.BLOCKCHAIN_NAME.value)
        blockchain_event = payload.get(EventConsumerEntity.BLOCKCHAIN_EVENT.value)

        if not blockchain_name or not blockchain_event:
            logger.info(f"Either blockchain name={blockchain_name} or blockchain_event={blockchain_event}  is empty")
            raise InternalServerErrorException(error_code=ErrorCode.CONSUMER_EVENT_EMPTY.value,
                                               error_details=ErrorDetails[ErrorCode.CONSUMER_EVENT_EMPTY.value].value)

        blockchain_detail = self.blockchain_service.get_blockchain(blockchain_name=blockchain_name)

        if not blockchain_detail:
            logger.info("Not supported blockchain")
            raise InternalServerErrorException(
                error_code=ErrorCode.UNSUPPORTED_BLOCKCHAIN_ON_SYSTEM.value,
                error_details=ErrorDetails[ErrorCode.UNSUPPORTED_BLOCKCHAIN_ON_SYSTEM.value].value)

        blockchain_network_id = blockchain_detail.get(BlockchainEntities.CHAIN_ID.value)

        if blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower():
            event_type = blockchain_event.get(EthereumEventConsumerEntities.NAME.value)
            tx_hash = blockchain_event.get(EthereumEventConsumerEntities.DATA.value, {}) \
                                      .get(EthereumEventConsumerEntities.TRANSACTION_HASH.value)
        elif blockchain_name.lower() == BlockchainName.BINANCE.value.lower():
            event_type = blockchain_event.get(BinanceEventConsumerEntities.NAME.value)
            tx_hash = blockchain_event.get(BinanceEventConsumerEntities.DATA.value, {}) \
                                      .get(BinanceEventConsumerEntities.TRANSACTION_HASH.value)
        elif blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
            event_type = blockchain_event.get(CardanoEventConsumer.TRANSACTION_DETAIL.value, {})\
                                         .get(CardanoEventConsumer.TX_TYPE.value)
            tx_hash = blockchain_event.get(CardanoEventConsumer.TX_HASH.value)
        else:
            raise InternalServerErrorException(
                error_code=ErrorCode.UNHANDLED_BLOCKCHAIN_OPERATION.value,
                error_details=ErrorDetails[ErrorCode.UNHANDLED_BLOCKCHAIN_OPERATION.value].value)

        if not event_type or not tx_hash or blockchain_network_id is None or not blockchain_event or not blockchain_detail:
            raise InternalServerErrorException(error_code=ErrorCode.CONSUMER_EVENT_EMPTY.value,
                                               error_details=ErrorDetails[ErrorCode.CONSUMER_EVENT_EMPTY.value].value)

        validate_consumer_event_type(blockchain_name=blockchain_name, event_type=event_type)
        validate_tx_hash_presence_in_blockchain(blockchain_name=blockchain_name, tx_hash=tx_hash,
                                                network_id=blockchain_network_id)
        self.process_event_consumer(event_type=event_type, tx_hash=tx_hash, network_id=blockchain_network_id,
                                    blockchain_event=blockchain_event, blockchain_detail=blockchain_detail)

    def process_event_consumer(self, event_type, tx_hash, network_id, blockchain_event, blockchain_detail):
        logger.info("Processing the event consumer payload")
        db_blockchain_name = blockchain_detail.get(BlockchainEntities.NAME.value).lower()
        required_block_confirmation = blockchain_detail.get(BlockchainEntities.BLOCK_CONFIRMATION.value)

        transaction = self.conversion_service.get_transaction_by_hash(tx_hash=tx_hash)

        validate_consumer_event_against_transaction(event_type=event_type, transaction=transaction,
                                                    blockchain_name=db_blockchain_name)

        if db_blockchain_name == BlockchainName.ETHEREUM.value.lower() and \
                event_type in [EthereumEventType.TOKEN_BURNT.value, EthereumEventType.TOKEN_MINTED.value]:
            json_str = blockchain_event.get(EthereumEventConsumerEntities.DATA.value, {}) \
                                       .get(EthereumEventConsumerEntities.JSON_STR.value)
            metadata = ast.literal_eval(json_str)

            tx_amount = metadata.get(EthereumEventConsumerEntities.AMOUNT.value)
            conversion_id = metadata.get(EthereumEventConsumerEntities.CONVERSION_ID.value).decode("utf-8")
            token_holder = metadata.get(EthereumEventConsumerEntities.TOKEN_HOLDER.value)

            conversion = self.process_evm_event(event_type=event_type, tx_hash=tx_hash, tx_amount=tx_amount,
                                                conversion_id=conversion_id, transaction=transaction,
                                                token_holder=token_holder)
        elif db_blockchain_name == BlockchainName.BINANCE.value.lower() and \
                event_type in [BinanceEventType.TOKEN_BURNT.value, BinanceEventType.TOKEN_MINTED.value]:
            json_str = blockchain_event.get(BinanceEventConsumerEntities.DATA.value, {}) \
                                       .get(BinanceEventConsumerEntities.JSON_STR.value)
            metadata = ast.literal_eval(json_str)

            tx_amount = metadata.get(EthereumEventConsumerEntities.AMOUNT.value)
            conversion_id = metadata.get(EthereumEventConsumerEntities.CONVERSION_ID.value).decode("utf-8")
            token_holder = metadata.get(EthereumEventConsumerEntities.TOKEN_HOLDER.value)

            conversion = self.process_evm_event(event_type=event_type, tx_hash=tx_hash, tx_amount=tx_amount,
                                                conversion_id=conversion_id, transaction=transaction,
                                                token_holder=token_holder)
        elif db_blockchain_name == BlockchainName.CARDANO.value.lower():
            if event_type == CardanoEventType.TOKEN_RECEIVED.value:
                conversion = self.process_cardano_token_received_event(blockchain_event=blockchain_event,
                                                                       transaction=transaction)
            elif transaction and event_type in [CardanoEventType.TOKEN_MINTED.value, CardanoEventType.TOKEN_BURNT.value]:
                conversion = self.conversion_service.get_conversion_detail_by_tx_id(
                    tx_id=transaction.get(TransactionEntities.ID.value))
            else:
                logger.info(f"Invalid event type provided ={event_type}")
                raise BadRequestException(error_code=ErrorCode.UNEXPECTED_EVENT_TYPE.value,
                                          error_details=ErrorDetails[ErrorCode.UNEXPECTED_EVENT_TYPE.value].value)
        else:
            logger.info(f"Invalid event type provided ={event_type}")
            raise BadRequestException(error_code=ErrorCode.UNEXPECTED_EVENT_TYPE.value,
                                      error_details=ErrorDetails[ErrorCode.UNEXPECTED_EVENT_TYPE.value].value)

        if transaction is None:
            transaction = self.conversion_service.get_transaction_by_hash(tx_hash=tx_hash)

        self.check_and_update_block_confirmation(tx_id=transaction.get(TransactionEntities.ID.value),
                                                 blockchain_name=db_blockchain_name,
                                                 required_block_confirmation=required_block_confirmation,
                                                 tx_hash=tx_hash, network_id=network_id)

        self.conversion_service.update_transaction_by_id(tx_id=transaction.get(TransactionEntities.ID.value),
                                                         tx_status=TransactionStatus.SUCCESS.value)

        conversion_id = conversion.get(ConversionEntities.ID.value)
        logger.info(f"Conversion id= {conversion_id}")
        conversion_complete_detail = self.conversion_service.get_conversion_complete_detail(conversion_id=conversion_id)

        if not conversion_complete_detail:
            logger.info("Invalid conversion id provided")
            raise InternalServerErrorException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                               error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        activity_event = get_next_activity_event_on_conversion(conversion_complete_detail=conversion_complete_detail)

        if activity_event:
            # Getting message pool id
            message_group = self.pool_service.get_message_group_pool()
            if message_group:
                message_group_id = message_group.get(MessagePoolEntities.MESSAGE_GROUP_ID.value)
            else:
                message_group_id = MESSAGE_GROUP_ID

            queue = QueueName.CONVERTER_BRIDGE.value
            if message_group_id in QueueName._value2member_map_:
                queue = QueueName[message_group_id].value

            NotificationService.send_message_to_queue(queue=queue,
                                                      message=json.dumps(activity_event),
                                                      message_group_id=message_group_id)
            if message_group:
                self.pool_service.update_message_pool(id=message_group.get(MessagePoolEntities.ID.value))
        else:
            conversion_transaction_id = conversion_complete_detail \
                .get(ConversionDetailEntities.TRANSACTIONS.value, {})[0] \
                .get(TransactionEntities.CONVERSION_TRANSACTION_ID.value)
            self.conversion_service.update_conversion_transaction(conversion_transaction_id=conversion_transaction_id,
                                                                  status=ConversionTransactionStatus.SUCCESS.value)
            self.conversion_service.update_conversion(conversion_id=conversion.get(ConversionEntities.ID.value),
                                                      status=ConversionStatus.SUCCESS.value)
            logger.info("Conversion is done")

    def process_evm_event(self, event_type, tx_hash, tx_amount, conversion_id, transaction, token_holder):

        if not tx_hash or not tx_amount or not conversion_id:
            raise InternalServerErrorException(
                error_code=ErrorCode.MISSING_ETHEREUM_EVENT_FIELDS.value,
                error_details=ErrorDetails[ErrorCode.MISSING_ETHEREUM_EVENT_FIELDS.value].value)
        try:
            conversion_detail = self.conversion_service.get_conversion_complete_detail(conversion_id=conversion_id)
        except Exception as e:
            logger.info(e)
            raise InternalServerErrorException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                               error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        if conversion_detail is None:
            raise InternalServerErrorException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                               error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        wallet_pair = conversion_detail.get(ConversionDetailEntities.WALLET_PAIR.value, {})
        conversion = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {})

        deposit_amount = conversion.get(ConversionEntities.DEPOSIT_AMOUNT.value)
        claim_amount = conversion.get(ConversionEntities.CLAIM_AMOUNT.value)
        fee_amount = conversion.get(ConversionEntities.FEE_AMOUNT.value)

        if event_type in [EthereumEventType.TOKEN_BURNT.value, BinanceEventType.TOKEN_BURNT.value]:
            if wallet_pair.get(WalletPairEntities.FROM_ADDRESS.value) != token_holder:
                logger.info(f"Mismatch on address from request and contract for {event_type} event")
                raise InternalServerErrorException(
                    error_code=ErrorCode.MISMATCH_TOKEN_HOLDER.value,
                    error_details=ErrorDetails[ErrorCode.MISMATCH_TOKEN_HOLDER.value].value)
        elif event_type in [EthereumEventType.TOKEN_MINTED.value, BinanceEventType.TOKEN_MINTED.value]:
            # TODO[BRIDGE-90] - DONE: Convert claim amount into right decimals | Already right decimals amount
            conversion_claim_amount = convert_str_to_decimal(claim_amount) + convert_str_to_decimal(fee_amount)
            if conversion_claim_amount != Decimal(tx_amount) or \
               wallet_pair.get(WalletPairEntities.TO_ADDRESS.value) != token_holder:
                logger.info(f"Mismatch on address and amount from request and contract for {event_type} event")
                raise InternalServerErrorException(error_code=ErrorCode.MISMATCH_AMOUNT.value,
                                                   error_details=ErrorDetails[ErrorCode.MISMATCH_AMOUNT.value].value)

        # TODO[BRIDGE-90] - DONE: Check this condition to provide right deposit amount | Already right decimals amount
        if event_type == EthereumEventType.TOKEN_BURNT.value and Decimal(float(deposit_amount)) != Decimal(tx_amount):
            token_pair_row_id = wallet_pair.get(WalletPairEntities.TOKEN_PAIR_ID.value)
            token_pair = self.token_service.get_token_pair_internal(token_pair_id=None,
                                                                    token_pair_row_id=token_pair_row_id)

            from_token_decimals = token_pair.get(TokenPairEntities.FROM_TOKEN.value) \
                                            .get(TokenEntities.ALLOWED_DECIMAL.value)
            to_token_decimals = token_pair.get(TokenPairEntities.TO_TOKEN.value) \
                                          .get(TokenEntities.ALLOWED_DECIMAL.value)

            fee_amount = Decimal(0)
            if token_pair.get(TokenPairEntities.CONVERSION_FEE.value):
                if from_token_decimals != to_token_decimals:
                    # Conversion fee temporary not allowed for token pairs with different decimals amount
                    raise BadRequestException(
                        error_code=ErrorCode.CONVERSION_FEE_NOT_ALLOWED.value,
                        error_details=ErrorDetails[ErrorCode.CONVERSION_FEE_NOT_ALLOWED.value].value)
                fee_amount = calculate_fee_amount(
                    amount=convert_str_to_decimal(value=tx_amount),
                    percentage=token_pair.get(TokenPairEntities.CONVERSION_FEE.value)
                                         .get(ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value))
            # TODO[BRIDGE-90] - DONE: Check this moment with calculation of conversion claim amount
            claim_amount = update_decimal_places(Decimal(tx_amount) - fee_amount,
                                                 from_decimals=from_token_decimals,
                                                 to_decimals=to_token_decimals)
            self.conversion_service.update_conversion(conversion_id=conversion_id, deposit_amount=tx_amount,
                                                      fee_amount=fee_amount, claim_amount=claim_amount)

        if not transaction:
            transaction = self.conversion_service.create_transaction_for_conversion(conversion_id=conversion_id,
                                                                                    transaction_hash=tx_hash,
                                                                                    created_by=CreatedBy.BACKEND.value)

        if transaction.get(TransactionEntities.STATUS.value) == TransactionStatus.SUCCESS.value:
            raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_PROCESSED.value,
                                      error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_PROCESSED.value].value)

        return conversion

    def process_cardano_token_received_event(self, blockchain_event, transaction):
        created_by = CreatedBy.BACKEND.value
        fee_amount = Decimal(0)
        tx_hash = blockchain_event.get(CardanoEventConsumer.TX_HASH.value)
        deposit_address = blockchain_event.get(CardanoEventConsumer.ADDRESS.value)
        tx_amount = blockchain_event.get(CardanoEventConsumer.TRANSACTION_DETAIL.value, {}).get(
            CardanoEventConsumer.TX_AMOUNT.value)
        policy_id = blockchain_event.get(CardanoEventConsumer.ASSET.value, {}).get(CardanoEventConsumer.POLICY_ID.value)
        asset_name = blockchain_event.get(CardanoEventConsumer.ASSET.value, {}).get(
            CardanoEventConsumer.ASSET_NAME.value)

        if deposit_address is None or tx_amount is None or tx_hash is None:
            raise InternalServerErrorException(
                error_code=ErrorCode.MISSING_CARDANO_EVENT_FIELDS.value,
                error_details=ErrorDetails[ErrorCode.MISSING_CARDANO_EVENT_FIELDS.value].value)

        if transaction is None:

            wallet_pair = self.wallet_pair_service.get_wallet_pair_by_deposit_address(deposit_address=deposit_address)
            if wallet_pair is None:
                logger.info("Wallet pair doesn't exist")
                raise BadRequestException(error_code=ErrorCode.WALLET_PAIR_NOT_EXISTS.value,
                                          error_details=ErrorDetails[ErrorCode.WALLET_PAIR_NOT_EXISTS.value].value)

            token_pair = self.token_service.get_token_pair_internal(
                token_pair_id=None,
                token_pair_row_id=wallet_pair.get(WalletPairEntities.TOKEN_PAIR_ID.value))

            from_token_decimals = token_pair.get(TokenPairEntities.FROM_TOKEN.value) \
                                            .get(TokenEntities.ALLOWED_DECIMAL.value)
            to_token_decimals = token_pair.get(TokenPairEntities.TO_TOKEN.value) \
                                          .get(TokenEntities.ALLOWED_DECIMAL.value)

            validate_conversion_request_amount(amount=tx_amount,
                                               min_value=token_pair.get(TokenPairEntities.MIN_VALUE.value),
                                               max_value=token_pair.get(TokenPairEntities.MAX_VALUE.value))

            token_address = token_pair.get(TokenPairEntities.FROM_TOKEN.value, {}) \
                                      .get(TokenEntities.TOKEN_ADDRESS.value)
            token_symbol = token_pair.get(TokenPairEntities.FROM_TOKEN.value, {}).get(TokenEntities.SYMBOL.value)

            if policy_id is None or asset_name is None or policy_id != token_address or \
                    asset_name != token_symbol.encode('utf-8').hex():
                raise BadRequestException(error_code=ErrorCode.INVALID_ASSET_TRANSFERRED.value,
                                          error_details=ErrorDetails[ErrorCode.INVALID_ASSET_TRANSFERRED.value].value)

            # TODO[BRIDGE-90] - DONE: Calculation of fee amount based on tx_amount | Works only for equal decimals
            tx_amount = Decimal(float(tx_amount))
            if token_pair.get(TokenPairEntities.CONVERSION_FEE.value):
                if from_token_decimals != to_token_decimals:
                    # Conversion fee temporary not allowed for token pairs with different decimals amount
                    raise BadRequestException(
                        error_code=ErrorCode.CONVERSION_FEE_NOT_ALLOWED.value,
                        error_details=ErrorDetails[ErrorCode.CONVERSION_FEE_NOT_ALLOWED.value].value)
                fee_amount = calculate_fee_amount(
                    amount=tx_amount,
                    percentage=token_pair.get(TokenPairEntities.CONVERSION_FEE.value)
                                         .get(ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value))

            from_blockchain_name = token_pair.get(TokenPairEntities.FROM_TOKEN.value) \
                                             .get(TokenEntities.BLOCKCHAIN.value) \
                                             .get(BlockchainEntities.NAME.value)

            # TODO[BRIDGE-90] - DONE: Passing params to calculate claim

            # Check that received amount can be converted to claim amount
            if from_token_decimals != to_token_decimals:
                corrected_tx_amount = reset_decimal_places(tx_amount,
                                                           from_decimals=from_token_decimals,
                                                           to_decimals=to_token_decimals)
                if corrected_tx_amount != tx_amount:
                    logger.error(f"Received token amount {tx_amount} cannot be converted for claim because of "
                                 f"difference in tokens decimals {from_token_decimals} > {to_token_decimals}")
                    raise BadRequestException(
                        error_code=ErrorCode.INVALID_CONVERSION_AMOUNT_PROVIDED.value,
                        error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_AMOUNT_PROVIDED.value].value)

            conversion = self.conversion_service.process_conversion_request(
                wallet_pair_id=wallet_pair.get(WalletPairEntities.ROW_ID.value),
                deposit_amount=tx_amount, fee_amount=fee_amount,
                from_blockchain_name=from_blockchain_name,
                from_token_decimals=from_token_decimals, to_token_decimals=to_token_decimals,
                created_by=created_by)
            try:
                transaction = self.conversion_service.create_transaction_for_conversion(
                    conversion_id=conversion.get(ConversionEntities.ID.value),
                    transaction_hash=tx_hash, created_by=created_by)

                self.conversion_service.update_transaction_by_id(
                    tx_id=transaction.get(TransactionEntities.ID.value),
                    tx_operation=TransactionOperation.TOKEN_RECEIVED.value,
                    tx_visibility=TransactionVisibility.EXTERNAL.value,
                    tx_amount=tx_amount,
                    tx_status=TransactionStatus.WAITING_FOR_CONFIRMATION.value)
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
        else:
            conversion = self.conversion_service.get_conversion_detail_by_tx_id(
                tx_id=transaction.get(TransactionEntities.ID.value))

        return conversion

    def check_and_update_block_confirmation(self, tx_id, blockchain_name, required_block_confirmation,
                                            tx_hash, network_id):

        current_block_confirmation = get_current_block_confirmation(blockchain_name=blockchain_name, tx_hash=tx_hash,
                                                                    network_id=network_id)
        if required_block_confirmation > current_block_confirmation:
            logger.info(f"Block confirmation is not enough as required confirmation={required_block_confirmation} "
                        f"and current_confirmation={current_block_confirmation}")
            self.conversion_service.update_transaction_by_id(tx_id=tx_id, confirmation=current_block_confirmation)
            current_block_confirmation = get_current_block_confirmation(blockchain_name=blockchain_name,
                                                                        tx_hash=tx_hash, network_id=network_id)

        logger.info(f"Current block confirmation={current_block_confirmation}")
        self.conversion_service.update_transaction_by_id(tx_id=tx_id, confirmation=current_block_confirmation)

        if current_block_confirmation < required_block_confirmation:
            raise BlockConfirmationNotEnoughException(
                error_code=ErrorCode.NOT_ENOUGH_BLOCK_CONFIRMATIONS.value,
                error_details=ErrorDetails[ErrorCode.NOT_ENOUGH_BLOCK_CONFIRMATIONS.value].value)

    @bridge_exception_handler(SLACK_HOOK=SLACK_HOOK, logger=logger)
    def converter_bridge(self, payload):
        logger.info(f"Converter bridge received the payload={payload}")
        blockchain_name = payload.get(ConverterBridgeEntities.BLOCKCHAIN_NAME.value)
        blockchain_event = payload.get(ConverterBridgeEntities.BLOCKCHAIN_EVENT.value, {})

        conversion_id = blockchain_event.get(ConverterBridgeEntities.CONVERSION_ID.value)
        tx_amount = blockchain_event.get(ConverterBridgeEntities.TX_AMOUNT.value)
        tx_operation = blockchain_event.get(ConverterBridgeEntities.TX_OPERATION.value)

        if not blockchain_name or not conversion_id or not tx_amount or not tx_operation \
                or tx_operation not in ALLOWED_CONVERTER_BRIDGE_TX_OPERATIONS:
            logger.info(f"Required field(s) blockchain_name={blockchain_name}, conversion_id={conversion_id}, "
                        f"tx_amount={tx_amount}, tx_operation={tx_operation} are missing or invalid values provided")
            raise InternalServerErrorException(
                error_code=ErrorCode.MISSING_CONVERTER_BRIDGE_FIELDS.value,
                error_details=ErrorDetails[ErrorCode.MISSING_CONVERTER_BRIDGE_FIELDS.value].value)

        conversion_complete_detail = self.conversion_service.get_conversion_complete_detail(conversion_id=conversion_id)
        if not conversion_complete_detail:
            logger.info(f"Invalid conversion_id={conversion_id} provided")
            raise InternalServerErrorException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                               error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        activity_event = get_next_activity_event_on_conversion(conversion_complete_detail=conversion_complete_detail)

        if payload == activity_event:
            self.process_converter_bridge_request(
                conversion_complete_detail=conversion_complete_detail,
                payload=payload)
            logger.info("Successfully processed the request")
        else:
            logger.info("Unable to match the request activity event")
            raise BadRequestException(error_code=ErrorCode.ACTIVITY_EVENT_NOT_MATCHING.value,
                                      error_details=ErrorDetails[ErrorCode.ACTIVITY_EVENT_NOT_MATCHING.value].value)

    def process_converter_bridge_request(self, conversion_complete_detail, payload):
        logger.info("Processing the conversion bridge request")
        db_from_blockchain = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {}) \
                                                       .get(TokenEntities.BLOCKCHAIN.value, {})
        db_from_blockchain_name = db_from_blockchain.get(BlockchainEntities.NAME.value).lower()

        db_to_blockchain = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}) \
                                                     .get(TokenEntities.BLOCKCHAIN.value, {})
        db_to_blockchain_name = db_to_blockchain.get(BlockchainEntities.NAME.value).lower()

        transactions = conversion_complete_detail.get(ConversionDetailEntities.TRANSACTIONS.value, [])
        payload_blockchain_name = payload.get(ConverterBridgeEntities.BLOCKCHAIN_NAME.value).lower()

        from_token_decimals = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {}) \
                                                        .get(TokenEntities.ALLOWED_DECIMAL.value)
        to_token_decimals = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}) \
                                                      .get(TokenEntities.ALLOWED_DECIMAL.value)

        target_token = {}
        target_blockchain = {}

        # Getting tx operation on which token side
        if payload_blockchain_name == db_from_blockchain_name:
            target_token = conversion_complete_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {})
            target_blockchain = db_from_blockchain
        elif payload_blockchain_name == db_to_blockchain_name:
            target_token = conversion_complete_detail.get(ConversionDetailEntities.TO_TOKEN.value, {})
            target_blockchain = db_to_blockchain

        network_id = target_blockchain.get(BlockchainEntities.CHAIN_ID.value)

        blockchain_event = payload.get(ConverterBridgeEntities.BLOCKCHAIN_EVENT.value)
        tx_amount = blockchain_event.get(ConverterBridgeEntities.TX_AMOUNT.value)
        tx_operation = blockchain_event.get(ConverterBridgeEntities.TX_OPERATION.value)

        tx_hash = None
        conversion_id = conversion_complete_detail.get(ConversionDetailEntities.CONVERSION.value) \
                                                  .get(ConversionEntities.ID.value)

        if payload_blockchain_name == BlockchainName.CARDANO.value.lower() and tx_operation == TransactionOperation.TOKEN_BURNT.value:
            address = conversion_complete_detail.get(ConversionDetailEntities.WALLET_PAIR.value, {}) \
                                                .get(WalletPairEntities.FROM_ADDRESS.value)
            tx_details = CardanoService.generate_transaction_detail(
                hash=transactions[0].get(TransactionEntities.TRANSACTION_HASH.value),
                environment=db_from_blockchain_name)
            deposit_address_details = generate_deposit_address_details_for_cardano_operation(
                wallet_pair=conversion_complete_detail.get(ConversionDetailEntities.WALLET_PAIR.value, {}))
            response = CardanoService.burn_token(conversion_id=conversion_id,
                                                 token=target_token.get(TokenEntities.SYMBOL.value),
                                                 tx_amount=tx_amount, tx_details=tx_details,
                                                 address=address, deposit_address_details=deposit_address_details)
            data = response.get(CardanoAPIEntities.DATA.value)
            if not data:
                raise InternalServerErrorException(
                    error_code=ErrorCode.DATA_NOT_AVAILABLE_ON_DERIVED_ADDRESS.value,
                    error_details=ErrorDetails[ErrorCode.DATA_NOT_AVAILABLE_ON_DERIVED_ADDRESS.value].value)

            tx_id = data.get(CardanoAPIEntities.TRANSACTION_ID.value)
            if not tx_id or not tx_id.strip():
                raise InternalServerErrorException(
                    error_code=ErrorCode.TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API.value,
                    error_details=ErrorDetails[ErrorCode.TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API.value].value)
            tx_hash = tx_id.strip()
        elif payload_blockchain_name == BlockchainName.CARDANO.value.lower() and tx_operation == TransactionOperation.TOKEN_MINTED.value:
            tx_details = CardanoService.generate_transaction_detail(
                hash=transactions[0].get(TransactionEntities.TRANSACTION_HASH.value),
                environment=db_from_blockchain_name)
            address = conversion_complete_detail.get(ConversionDetailEntities.WALLET_PAIR.value, {}) \
                                                .get(WalletPairEntities.TO_ADDRESS.value)
            source_address = conversion_complete_detail.get(ConversionDetailEntities.WALLET_PAIR.value, {}) \
                                                       .get(WalletPairEntities.FROM_ADDRESS.value)

            conversion_fee_amount = conversion_complete_detail.get(ConversionDetailEntities.CONVERSION.value) \
                                                              .get(ConversionEntities.FEE_AMOUNT.value)

            # TODO[BRIDGE-90] - DONE: Provide info about token decimals difference
            decimals_difference = from_token_decimals - to_token_decimals
            response = CardanoService.mint_token(conversion_id=conversion_id,
                                                 token=target_token.get(TokenEntities.SYMBOL.value),
                                                 tx_amount=tx_amount, tx_details=tx_details, address=address,
                                                 source_address=source_address, fee=conversion_fee_amount,
                                                 decimals_difference=decimals_difference)
            data = response.get(CardanoAPIEntities.DATA.value)
            if not data:
                raise InternalServerErrorException(
                    error_code=ErrorCode.DATA_NOT_AVAILABLE_ON_DERIVED_ADDRESS.value,
                    error_details=ErrorDetails[ErrorCode.DATA_NOT_AVAILABLE_ON_DERIVED_ADDRESS.value].value)

            tx_id = data.get(CardanoAPIEntities.TRANSACTION_ID.value)
            if not tx_id or not tx_id.strip():
                raise InternalServerErrorException(
                    error_code=ErrorCode.TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API.value,
                    error_details=ErrorDetails[ErrorCode.TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API.value].value)
            tx_hash = tx_id.strip()
        elif payload_blockchain_name == BlockchainName.ETHEREUM.value.lower() and tx_operation == TransactionOperation.TOKEN_MINTED.value:
            status = conversion_complete_detail.get(ConversionDetailEntities.CONVERSION.value, {}) \
                                               .get(ConversionEntities.STATUS.value)
            if status != ConversionStatus.PROCESSING.value:
                raise BadRequestException(
                    error_code=ErrorCode.TRANSACTION_ALREADY_PROCESSED.value,
                    error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_PROCESSED.value].value)

            # TODO[BRIDGE-90] - DONE: Updating conversion with new claim amount | Already right claim amount
            self.conversion_service.update_conversion(
                conversion_id=conversion_complete_detail.get(ConversionDetailEntities.CONVERSION.value, {})
                                                        .get(ConversionEntities.ID.value),
                claim_amount=tx_amount, status=ConversionStatus.WAITING_FOR_CLAIM.value)
        elif payload_blockchain_name == BlockchainName.BINANCE.value.lower() and tx_operation == TransactionOperation.TOKEN_MINTED.value:
            status = conversion_complete_detail.get(ConversionDetailEntities.CONVERSION.value, {}) \
                                               .get(ConversionEntities.STATUS.value)
            if status != ConversionStatus.PROCESSING.value:
                raise BadRequestException(
                    error_code=ErrorCode.TRANSACTION_ALREADY_PROCESSED.value,
                    error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_PROCESSED.value].value)

            # TODO[BRIDGE-90] - DONE: Updating conversion with new claim amount | Already right claim amount
            self.conversion_service.update_conversion(
                conversion_id=conversion_complete_detail.get(ConversionDetailEntities.CONVERSION.value, {})
                                                        .get(ConversionEntities.ID.value),
                claim_amount=tx_amount, status=ConversionStatus.WAITING_FOR_CLAIM.value)
        else:
            logger.info("Invalid tx_operation provided")
            raise InternalServerErrorException(
                error_code=ErrorCode.INVALID_TRANSACTION_OPERATION_PROVIDED.value,
                error_details=ErrorDetails[ErrorCode.INVALID_TRANSACTION_OPERATION_PROVIDED.value].value)

        if payload_blockchain_name == BlockchainName.CARDANO.value.lower() \
                and (tx_operation in [TransactionOperation.TOKEN_BURNT.value, TransactionOperation.TOKEN_MINTED.value]):
            self.conversion_service.create_transaction(
                conversion_transaction_id=transactions[0].get(TransactionEntities.CONVERSION_TRANSACTION_ID.value),
                token_id=target_token.get(TokenEntities.ROW_ID.value),
                transaction_visibility=TransactionVisibility.EXTERNAL.value,
                transaction_operation=tx_operation, transaction_hash=tx_hash,
                transaction_amount=tx_amount, confirmation=0,
                status=TransactionStatus.WAITING_FOR_CONFIRMATION.value,
                created_by=CreatedBy.BACKEND.value)

            wait_until_transaction_hash_exists_in_blockchain(tx_hash, network_id)
