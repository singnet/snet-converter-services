from decimal import Decimal

from application.service.conversion_reponse import get_latest_user_pending_conversion_request_response, \
    create_conversion_response, create_conversion_request_response, \
    get_conversion_detail_response, get_conversion_history_response, create_conversion_transaction_response, \
    create_transaction_response, create_transaction_for_conversion_response, get_transaction_by_hash_response, \
    claim_conversion_response, \
    get_conversion_response, update_conversion_response
from application.service.token_service import TokenService
from application.service.wallet_pair_service import WalletPairService
from common.logger import get_logger
from constants.entity import TokenPairEntities, WalletPairEntities, \
    ConversionEntities, TokenEntities, BlockchainEntities, ConversionDetailEntities, TransactionConversionEntities, \
    TransactionEntities, ConversionFeeEntities, ConverterBridgeEntities, EventConsumerEntity
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, CreatedBy, SignatureTypeEntities, ConversionOn
from constants.status import ConversionStatus, TransactionVisibility, TransactionStatus
from infrastructure.repositories.conversion_repository import ConversionRepository
from utils.blockchain import validate_address, validate_conversion_claim_request_signature, \
    calculate_fee_amount, \
    validate_conversion_request_amount, convert_str_to_decimal, get_next_activity_event_on_conversion, \
    check_existing_transaction_state, validate_ethereum_transaction_details_against_conversion, \
    validate_cardano_transaction_details_against_conversion
from utils.exceptions import BadRequestException, InternalServerErrorException
from utils.general import get_blockchain_from_token_pair_details, get_response_from_entities, paginate_items, \
    is_supported_network_conversion
from utils.signature import validate_conversion_signature, get_signature

logger = get_logger(__name__)


class ConversionService:

    def __init__(self):
        self.conversion_repo = ConversionRepository()
        self.token_service = TokenService()
        self.wallet_pair_service = WalletPairService()

    def create_conversion(self, wallet_pair_id, deposit_amount, fee_amount, claim_amount,
                          created_by=CreatedBy.DAPP.value):
        logger.info(f"Creating the conversion with wallet_pair_id={wallet_pair_id}, deposit_amount={deposit_amount}, "
                    f" fee_amount={fee_amount} claim_amount={claim_amount} created_by={created_by}")
        conversion = self.conversion_repo.create_conversion(wallet_pair_id=wallet_pair_id,
                                                            deposit_amount=deposit_amount, fee_amount=fee_amount,
                                                            claim_amount=claim_amount, created_by=created_by)
        return create_conversion_response(conversion.to_dict())

    def create_conversion_transaction(self, conversion_id, created_by):
        logger.info(f"Creating the conversion transaction = {conversion_id}, created_by={created_by}")
        conversion_transaction = self.conversion_repo.create_conversion_transaction(conversion_id=conversion_id,
                                                                                    created_by=created_by)
        return create_conversion_transaction_response(conversion_transaction.to_dict())

    def create_transaction(self, conversion_transaction_id, from_token_id, to_token_id, transaction_visibility,
                           transaction_operation, transaction_hash, transaction_amount, confirmation, status,
                           created_by):
        logger.info(f"Creating the transaction with the details conversion_transaction_id={conversion_transaction_id},"
                    f" from_token_id={from_token_id}, to_token_id={to_token_id}, transaction_visibility="
                    f"{transaction_visibility}, transaction_operation={transaction_operation}, "
                    f"transaction_hash={transaction_hash}, transaction_amount={transaction_amount}, "
                    f" confirmation={confirmation}, status={status}, created_by={created_by}")
        transaction = self.conversion_repo.create_transaction(conversion_transaction_id=conversion_transaction_id,
                                                              from_token_id=from_token_id, to_token_id=to_token_id,
                                                              transaction_visibility=transaction_visibility,
                                                              transaction_operation=transaction_operation,
                                                              transaction_hash=transaction_hash,
                                                              transaction_amount=transaction_amount,
                                                              confirmation=confirmation, status=status,
                                                              created_by=created_by)
        return create_transaction_response(transaction.to_dict())

    def get_conversion(self, conversion_id):
        logger.info(f"Getting the conversion for the conversion_id={conversion_id} ")
        conversion = self.get_conversion_complete_detail(conversion_id=conversion_id)

        if conversion is None:
            raise BadRequestException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                      error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        return get_conversion_response(conversion)

    def get_conversion_detail_by_tx_id(self, tx_id):
        logger.info(f"Get the conversion detail by tx_id={tx_id}")
        conversion = self.conversion_repo.get_conversion_detail_by_tx_id(tx_id)
        return conversion.to_dict()

    def get_conversion_detail(self, conversion_id):
        logger.info(f"Get the conversion for the ID={conversion_id}")
        conversion_detail = self.conversion_repo.get_conversion_detail(conversion_id=conversion_id)

        if conversion_detail is None:
            raise BadRequestException(error_code=ErrorCode.INVALID_CONVERSION_ID.value,
                                      error_details=ErrorDetails[ErrorCode.INVALID_CONVERSION_ID.value].value)

        return get_conversion_detail_response(conversion_detail.to_dict())

    def get_latest_user_pending_conversion_request(self, wallet_pair_id):
        conversion = self.conversion_repo.get_latest_user_pending_conversion_request(wallet_pair_id=wallet_pair_id,
                                                                                     status=ConversionStatus.USER_INITIATED.value)
        return get_latest_user_pending_conversion_request_response(conversion.to_dict()) if conversion else None

    def update_conversion_status(self, conversion_id, status):
        logger.info(f"Updating the conversion status for the conversion_id={conversion_id}, "
                    f"status={status}")
        self.conversion_repo.update_conversion_status(conversion_id=conversion_id, status=status)

    def update_conversion(self, conversion_id, deposit_amount=None, claim_amount=None, fee_amount=None, status=None,
                          claim_signature=None):
        logger.info(f"Updating the conversion  for the conversion_id={conversion_id}, "
                    f"deposit_amount={deposit_amount}, claim_amount={claim_amount}, fee_amount={fee_amount}, "
                    f"status={status}, claim_signature={claim_signature}")
        conversion = self.conversion_repo.update_conversion(conversion_id=conversion_id, deposit_amount=deposit_amount,
                                                            claim_amount=claim_amount, fee_amount=fee_amount,
                                                            status=status, claim_signature=claim_signature)
        return update_conversion_response(conversion.to_dict())

    def update_conversion_transaction(self, conversion_transaction_id, status):
        logger.info(
            f"Updating the conversion transaction for the conversion_transaction_id={conversion_transaction_id}, "
            f"status={status}")
        self.conversion_repo.update_conversion_transaction(conversion_transaction_id=conversion_transaction_id,
                                                           status=status)

    @staticmethod
    def create_conversion_request_validation(token_pair_id, amount, from_address, to_address, block_number,
                                             signature, token_pair):
        logger.info("Validation the conversion request")
        is_signer_as_from_address = False
        from_blockchain = get_blockchain_from_token_pair_details(token_pair=token_pair,
                                                                 blockchain_conversion_type=TokenPairEntities.FROM_TOKEN.value)
        to_blockchain = get_blockchain_from_token_pair_details(token_pair=token_pair,
                                                               blockchain_conversion_type=TokenPairEntities.TO_TOKEN.value)

        if not is_supported_network_conversion(from_blockchain=from_blockchain, to_blockchain=to_blockchain):
            logger.exception(
                f"Unsupported network conversion detected from_blockchain={from_blockchain}, to_blockchain={to_blockchain}")
            raise InternalServerErrorException(error_code=ErrorCode.UNSUPPORTED_CHAIN_ID.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNSUPPORTED_CHAIN_ID.value].value)

        from_blockchain_name = from_blockchain.get(BlockchainEntities.NAME.value)

        if from_blockchain_name.lower() == BlockchainName.ETHEREUM.value.lower():
            is_signer_as_from_address = True
            chain_id = from_blockchain.get(BlockchainEntities.CHAIN_ID.value)
        else:
            chain_id = to_blockchain.get(BlockchainEntities.CHAIN_ID.value)

        result = validate_conversion_signature(token_pair_id=token_pair_id, amount=amount, from_address=from_address,
                                               to_address=to_address, block_number=block_number, signature=signature,
                                               is_signer_as_from_address=is_signer_as_from_address, chain_id=chain_id)
        if result is False:
            raise BadRequestException(error_code=ErrorCode.INCORRECT_SIGNATURE.value,
                                      error_details=ErrorDetails[ErrorCode.INCORRECT_SIGNATURE.value].value)

        validate_address(from_address=from_address, to_address=to_address, from_blockchain=from_blockchain,
                         to_blockchain=to_blockchain)

    def create_conversion_request(self, token_pair_id, amount, from_address, to_address, block_number, signature):
        logger.info(f"Creating the conversion request for token_pair_id={token_pair_id}, amount={amount}, "
                    f"from_address={from_address}, to_address={to_address}, block_number={block_number}, "
                    f"signature={signature}")
        contract_signature = None
        fee_amount = Decimal(0)
        contract_address = None

        token_pair = self.token_service.get_token_pair_internal(token_pair_id=token_pair_id)

        validate_conversion_request_amount(amount=amount,
                                           min_value=token_pair.get(TokenPairEntities.MIN_VALUE.value),
                                           max_value=token_pair.get(TokenPairEntities.MAX_VALUE.value))

        ConversionService.create_conversion_request_validation(token_pair_id=token_pair_id, amount=amount,
                                                               from_address=from_address, to_address=to_address,
                                                               block_number=block_number, signature=signature,
                                                               token_pair=token_pair)
        wallet_pair = self.wallet_pair_service.persist_wallet_pair_details(from_address=from_address,
                                                                           to_address=to_address, amount=amount,
                                                                           signature=signature,
                                                                           block_number=block_number,
                                                                           token_pair=token_pair)
        amount = convert_str_to_decimal(value=amount)

        if token_pair.get(TokenPairEntities.CONVERSION_FEE.value):
            fee_amount = calculate_fee_amount(amount=amount, percentage=token_pair.get(
                TokenPairEntities.CONVERSION_FEE.value).get(ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value))

        from_blockchain_name = token_pair.get(TokenPairEntities.FROM_TOKEN.value).get(
            TokenEntities.BLOCKCHAIN.value).get(BlockchainEntities.NAME.value)
        conversion = self.process_conversion_request(wallet_pair_id=wallet_pair.get(WalletPairEntities.ROW_ID.value),
                                                     deposit_amount=amount, fee_amount=fee_amount,
                                                     from_blockchain_name=from_blockchain_name)

        conversion_id = conversion[ConversionEntities.ID.value]
        deposit_address = wallet_pair[WalletPairEntities.DEPOSIT_ADDRESS.value]
        deposit_amount = conversion.get(ConversionEntities.DEPOSIT_AMOUNT.value)

        if not deposit_address:
            user_address = wallet_pair.get(WalletPairEntities.FROM_ADDRESS.value)
            contract_address = self.get_token_contract_address_for_conversion_id(conversion_id=conversion_id)
            contract_signature = get_signature(signature_type=SignatureTypeEntities.CONVERSION_OUT.value,
                                               user_address=user_address, conversion_id=conversion_id,
                                               amount=convert_str_to_decimal(deposit_amount),
                                               contract_address=contract_address,
                                               chain_id=token_pair.get(
                                                   TokenPairEntities.FROM_TOKEN.value).get(
                                                   TokenEntities.BLOCKCHAIN.value).get(
                                                   BlockchainEntities.CHAIN_ID.value))
        return create_conversion_request_response(conversion_id=conversion_id, deposit_address=deposit_address,
                                                  signature=contract_signature, deposit_amount=deposit_amount,
                                                  contract_address=contract_address)

    def validate_transaction_hash(self, conversion_detail, transaction_hash, created_by):
        transaction = self.get_transaction_by_hash(tx_hash=transaction_hash)

        if transaction:
            raise BadRequestException(error_code=ErrorCode.TRANSACTION_ALREADY_CREATED.value,
                                      error_details=ErrorDetails[ErrorCode.TRANSACTION_ALREADY_CREATED.value].value)

        transactions = conversion_detail.get(ConversionDetailEntities.TRANSACTIONS.value)
        conversion = conversion_detail.get(ConversionDetailEntities.CONVERSION.value)

        from_blockchain = conversion_detail.get(ConversionDetailEntities.FROM_TOKEN.value, {}).get(
            TokenEntities.BLOCKCHAIN.value, {})
        to_blockchain = conversion_detail.get(ConversionDetailEntities.TO_TOKEN.value, {}).get(
            TokenEntities.BLOCKCHAIN.value, {})

        if not is_supported_network_conversion(from_blockchain=from_blockchain, to_blockchain=to_blockchain):
            logger.exception(
                f"Unsupported network conversion detected from_blockchain={from_blockchain}, to_blockchain={to_blockchain}")
            raise InternalServerErrorException(error_code=ErrorCode.UNSUPPORTED_CHAIN_ID.value,
                                               error_details=ErrorDetails[ErrorCode.UNSUPPORTED_CHAIN_ID.value].value)

        next_activity = get_next_activity_event_on_conversion(conversion_complete_detail=conversion_detail)
        if next_activity is None:
            raise BadRequestException(error_code=ErrorCode.CONVERSION_ALREADY_DONE.value,
                                      error_details=ErrorDetails[ErrorCode.CONVERSION_ALREADY_DONE.value].value)

        if next_activity.get(ConverterBridgeEntities.BLOCKCHAIN_NAME.value).lower() == from_blockchain.get(
                BlockchainEntities.NAME.value).lower():
            conversion_on = ConversionOn.FROM.value
            blockchain = from_blockchain
        else:
            conversion_on = ConversionOn.TO.value
            blockchain = to_blockchain

        blockchain_name = blockchain.get(BlockchainEntities.NAME.value).lower()
        chain_id = blockchain.get(BlockchainEntities.CHAIN_ID.value)

        if created_by == CreatedBy.DAPP.value and blockchain_name.lower() == BlockchainName.CARDANO.value.lower():
            raise BadRequestException(error_code=ErrorCode.DAPP_AUTHORIZED_FOR_CARDANO_TX_UPDATE.value,
                                      error_details=ErrorDetails[
                                          ErrorCode.DAPP_AUTHORIZED_FOR_CARDANO_TX_UPDATE.value].value)

        check_existing_transaction_state(transactions=transactions, conversion_on=conversion_on)

        if blockchain_name == BlockchainName.ETHEREUM.value.lower():
            contract_address = self.get_token_contract_address_for_conversion_id(
                conversion_id=conversion.get(ConversionEntities.ID.value))
            validate_ethereum_transaction_details_against_conversion(chain_id=chain_id,
                                                                     transaction_hash=transaction_hash,
                                                                     conversion_on=conversion_on,
                                                                     contract_address=contract_address,
                                                                     conversion_detail=conversion_detail)
        elif blockchain_name == BlockchainName.CARDANO.value.lower():
            validate_cardano_transaction_details_against_conversion(chain_id=chain_id,
                                                                    transaction_hash=transaction_hash,
                                                                    conversion_on=conversion_on,
                                                                    conversion_detail=conversion_detail)
        return next_activity

    def process_conversion_request(self, wallet_pair_id: str, deposit_amount: Decimal, fee_amount: Decimal,
                                   from_blockchain_name, created_by: str = CreatedBy.DAPP.value):
        logger.info(f"Processing the conversion request with wallet_pair_id={wallet_pair_id},"
                    f" deposit_amount={deposit_amount}, fee_amount={fee_amount}, "
                    f"from_blockchain_name={from_blockchain_name}")
        conversion = None
        if from_blockchain_name != BlockchainName.ETHEREUM.value:
            conversion = self.get_latest_user_pending_conversion_request(wallet_pair_id=wallet_pair_id)

        if conversion:
            if Decimal(float(conversion.get(ConversionEntities.DEPOSIT_AMOUNT.value))) != deposit_amount or \
                    Decimal(float(conversion.get(ConversionEntities.FEE_AMOUNT.value))) != fee_amount:
                conversion = self.update_conversion(conversion_id=conversion[ConversionEntities.ID.value],
                                                    deposit_amount=deposit_amount, fee_amount=fee_amount,
                                                    claim_amount=deposit_amount - fee_amount)
        else:
            conversion = self.create_conversion(wallet_pair_id=wallet_pair_id, deposit_amount=deposit_amount,
                                                fee_amount=fee_amount, claim_amount=deposit_amount - fee_amount,
                                                created_by=created_by)
        return conversion

    def get_token_contract_address_for_conversion_id(self, conversion_id):
        logger.info(f"Getting the token contract address for conversion_id={conversion_id}")
        return self.conversion_repo.get_token_contract_address_for_conversion_id(conversion_id)

    def get_conversion_history(self, address, page_size, page_number):
        logger.info(f"Getting the conversion history for the given address={address}, page_size={page_size}, "
                    f"page_number={page_number}")
        conversion_detail_history = self.conversion_repo.get_conversion_history(address=address, conversion_id=None)
        conversion_detail_history_response = get_conversion_history_response(
            get_response_from_entities(conversion_detail_history))
        return paginate_items(items=conversion_detail_history_response, page_number=page_number, page_size=page_size)

    def get_conversion_complete_detail(self, conversion_id):
        logger.info(f"Getting the conversion complete detail")
        conversion_detail_history = self.conversion_repo.get_conversion_history(address=None,
                                                                                conversion_id=conversion_id)
        conversion_detail_history_response = get_response_from_entities(conversion_detail_history)
        return conversion_detail_history_response[0] if len(conversion_detail_history_response) else None

    @staticmethod
    def get_conversion_ids_from_conversion_detail(conversion_detail):
        conversion_ids = []
        for conversion in conversion_detail:
            conversion_ids.append(conversion["conversion"]["id"])
        return set(conversion_ids)

    def create_transaction_for_conversion(self, conversion_id, transaction_hash, created_by=CreatedBy.DAPP.value):
        logger.info(f"Creating the new transaction for the conversion_id={conversion_id} with "
                    f"transaction_hash={transaction_hash}, created_by={created_by}")
        conversion_detail = self.get_conversion_detail(conversion_id=conversion_id)
        next_activity = self.validate_transaction_hash(conversion_detail=conversion_detail,
                                                       transaction_hash=transaction_hash, created_by=created_by)
        transaction = self.proces_transaction_creation(conversion_detail=conversion_detail,
                                                       transaction_hash=transaction_hash, next_activity=next_activity,
                                                       created_by=created_by)
        return create_transaction_for_conversion_response(transaction)

    def proces_transaction_creation(self, conversion_detail, transaction_hash, next_activity, created_by):
        transaction = conversion_detail.get(ConversionDetailEntities.TRANSACTIONS.value)
        conversion_row_id = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {}).get(
            ConversionEntities.ROW_ID.value)
        conversion_id = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {}).get(
            ConversionEntities.ID.value)

        transaction_operation = next_activity.get(EventConsumerEntity.BLOCKCHAIN_EVENT.value).get(
            ConverterBridgeEntities.TX_OPERATION.value)

        if not len(transaction):
            token_id = conversion_detail.get(ConversionDetailEntities.FROM_TOKEN.value).get(
                TokenEntities.ROW_ID.value)
            conversion_transaction = self.create_conversion_transaction(conversion_id=conversion_row_id,
                                                                        created_by=created_by)
            conversion_transaction_row_id = conversion_transaction.get(TransactionConversionEntities.ROW_ID.value)
            transaction_amount = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {}).get(
                ConversionEntities.DEPOSIT_AMOUNT.value)
        else:
            token_id = conversion_detail.get(ConversionDetailEntities.TO_TOKEN.value).get(
                TokenEntities.ROW_ID.value)
            conversion_transaction_row_id = transaction[0].get(TransactionEntities.CONVERSION_TRANSACTION_ID.value)
            transaction_amount = conversion_detail.get(ConversionDetailEntities.CONVERSION.value, {}).get(
                ConversionEntities.CLAIM_AMOUNT.value)

        if transaction_amount is None:
            raise BadRequestException(error_code=ErrorCode.UNSUPPORTED_CHAIN_ID.value,
                                      error_details=ErrorDetails[ErrorCode.UNSUPPORTED_CHAIN_ID.value].value)

        transaction = self.create_transaction(conversion_transaction_id=conversion_transaction_row_id,
                                              from_token_id=token_id, to_token_id=token_id,
                                              transaction_visibility=TransactionVisibility.EXTERNAL.value,
                                              transaction_operation=transaction_operation,
                                              transaction_hash=transaction_hash, transaction_amount=transaction_amount,
                                              confirmation=0, status=TransactionStatus.WAITING_FOR_CONFIRMATION.value,
                                              created_by=created_by)
        self.update_conversion_status(conversion_id=conversion_id, status=ConversionStatus.PROCESSING.value)

        return transaction

    def update_transaction_by_id(self, tx_id, tx_operation=None, tx_visibility=None, tx_amount=None, confirmation=None,
                                 tx_status=None, created_by=None):
        logger.info(
            f"Updating the transaction of tx_id={tx_id}, tx_operation={tx_operation}, tx_visibility={tx_visibility}, "
            f"tx_amount={tx_amount}, confirmation={confirmation}, tx_status={tx_status}, created_by={created_by}")
        self.conversion_repo.update_transaction_by_id(tx_id=tx_id, tx_operation=tx_operation,
                                                      tx_visibility=tx_visibility, tx_amount=tx_amount,
                                                      confirmation=confirmation, tx_status=tx_status,
                                                      created_by=created_by)

    def get_transaction_by_hash(self, tx_hash):
        logger.info(f"Getting the transaction by tx_hash={tx_hash}")
        transaction = self.conversion_repo.get_transaction_by_hash(tx_hash)
        return get_transaction_by_hash_response(transaction.to_dict()) if transaction else None

    def claim_conversion(self, conversion_id, amount, from_address, to_address, signature):
        logger.info(
            f"Claim the conversion for the conversion_id={conversion_id}, amount={amount}, from_address={from_address},"
            f"to_address={to_address}, signature={signature}")
        conversion_detail = self.get_conversion_detail(conversion_id=conversion_id)
        chain_id = conversion_detail.get(ConversionDetailEntities.TO_TOKEN.value).get(
            TokenEntities.BLOCKCHAIN.value).get(BlockchainEntities.CHAIN_ID.value)

        # validate the request signature
        validate_conversion_claim_request_signature(conversion_detail=conversion_detail, amount=amount,
                                                    from_address=from_address, to_address=to_address,
                                                    signature=signature, chain_id=chain_id)

        conversion = conversion_detail.get(ConversionDetailEntities.CONVERSION.value)
        claim_amount = conversion.get(ConversionEntities.CLAIM_AMOUNT.value)
        user_address = conversion_detail.get(ConversionDetailEntities.WALLET_PAIR.value).get(
            WalletPairEntities.TO_ADDRESS.value)
        contract_address = self.get_token_contract_address_for_conversion_id(conversion_id=conversion_id)

        # Generate claim signature
        claim_signature = get_signature(signature_type=SignatureTypeEntities.CONVERSION_IN.value,
                                        user_address=user_address, conversion_id=conversion_id,
                                        amount=Decimal(float(claim_amount)),
                                        contract_address=contract_address, chain_id=chain_id)
        # Update the signature and status
        self.update_conversion(conversion_id=conversion_id, claim_signature=claim_signature)

        return claim_conversion_response(signature=claim_signature, claim_amount=claim_amount,
                                         contract_address=contract_address)
