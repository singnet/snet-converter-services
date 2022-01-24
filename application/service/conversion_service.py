from application.service.conversion_reponse import get_latest_user_pending_conversion_request_response, \
    update_conversion_amount_response, create_conversion_response, create_conversion_request_response
from application.service.token_service import TokenService
from application.service.wallet_pair_service import WalletPairService
from common.logger import get_logger
from constants.entity import TokenPairEntities, WalletPairEntities, \
    ConversionEntities, TokenEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName
from constants.status import ConversionStatus
from infrastructure.repositories.conversion_repository import ConversionRepository
from utils.blockchain import validate_address, get_lowest_unit_amount
from utils.exceptions import BadRequestException
from utils.general import get_blockchain_name_from_token_pair_details

from utils.signature import validate_conversion_signature

logger = get_logger(__name__)


class ConversionService:

    def __init__(self):
        self.conversion_repo = ConversionRepository()
        self.token_service = TokenService()
        self.wallet_pair_service = WalletPairService()

    def create_conversion(self, wallet_pair_id, deposit_amount):
        logger.info(f"Creating the conversion with wallet_pair_id={wallet_pair_id}, deposit_amount={deposit_amount}")
        conversion = self.conversion_repo.create_conversion(wallet_pair_id=wallet_pair_id,
                                                            deposit_amount=deposit_amount)
        return create_conversion_response(conversion.to_dict())

    def get_latest_user_pending_conversion_request(self, wallet_pair_id):
        conversion = self.conversion_repo.get_latest_user_pending_conversion_request(wallet_pair_id=wallet_pair_id,
                                                                                     status=ConversionStatus.USER_INITIATED.value)
        return get_latest_user_pending_conversion_request_response(conversion.to_dict()) if conversion else None

    def update_conversion_amount(self, conversion_id, deposit_amount):
        logger.info(f"Updating the conversion amount for the conversion_id={conversion_id}, "
                    f"deposit_amount={deposit_amount}")
        conversion = self.conversion_repo.update_conversion_amount(conversion_id=conversion_id,
                                                                   deposit_amount=deposit_amount)
        return update_conversion_amount_response(conversion.to_dict()) if conversion else None

    @staticmethod
    def create_conversion_request_validation(token_pair_id, amount, from_address, to_address, block_number,
                                             signature, token_pair):
        logger.info("Validation the conversion request")
        is_signer_as_from_address = False
        from_blockchain_name = get_blockchain_name_from_token_pair_details(token_pair=token_pair,
                                                                           blockchain_conversion_type=TokenPairEntities.FROM_TOKEN.value)
        to_blockchain_name = get_blockchain_name_from_token_pair_details(token_pair=token_pair,
                                                                         blockchain_conversion_type=TokenPairEntities.TO_TOKEN.value)
        if from_blockchain_name == BlockchainName.ETHEREUM.value:
            is_signer_as_from_address = True

        result = validate_conversion_signature(token_pair_id=token_pair_id, amount=amount, from_address=from_address,
                                               to_address=to_address, block_number=block_number, signature=signature,
                                               is_signer_as_from_address=is_signer_as_from_address)
        if result is False:
            raise BadRequestException(error_code=ErrorCode.INCORRECT_SIGNATURE.value,
                                      error_details=ErrorDetails[ErrorCode.INCORRECT_SIGNATURE.value].value)

        validate_address(from_address=from_address, to_address=to_address, from_blockchain_name=from_blockchain_name,
                         to_blockchain_name=to_blockchain_name)

    def create_conversion_request(self, token_pair_id, amount, from_address, to_address, block_number, signature):
        logger.info(f"Creating the conversion request for token_pair_id={token_pair_id}, amount={amount}, "
                    f"from_address={from_address}, to_address={to_address}, block_number={block_number}, "
                    f"signature={signature}")
        token_pair = self.token_service.get_token_pair_internal(token_pair_id=token_pair_id)
        ConversionService().create_conversion_request_validation(token_pair_id=token_pair_id, amount=amount,
                                                                 from_address=from_address, to_address=to_address,
                                                                 block_number=block_number, signature=signature,
                                                                 token_pair=token_pair)
        wallet_pair = self.wallet_pair_service.persist_wallet_pair_details(from_address=from_address,
                                                                           to_address=to_address, amount=amount,
                                                                           signature=signature,
                                                                           block_number=block_number,
                                                                           token_pair=token_pair)
        allowed_decimal = token_pair.get(TokenPairEntities.FROM_TOKEN.value, {}).get(
            TokenEntities.ALLOWED_DECIMAL.value)

        # Always we store in the lowest unit in db
        lowest_unit_amount = get_lowest_unit_amount(amount, allowed_decimal)
        conversion = self.process_conversion_request(wallet_pair_id=wallet_pair.get(WalletPairEntities.ROW_ID.value),
                                                     deposit_amount=lowest_unit_amount)
        return create_conversion_request_response(wallet_pair, conversion)

    def process_conversion_request(self, wallet_pair_id, deposit_amount):
        logger.info(f"Processing the conversion request with wallet_pair_id={wallet_pair_id},"
                    f" deposit_amount={deposit_amount}")
        conversion = self.get_latest_user_pending_conversion_request(wallet_pair_id=wallet_pair_id)

        if conversion:
            conversion = self.update_conversion_amount(conversion_id=conversion[ConversionEntities.ID.value],
                                                       deposit_amount=deposit_amount)
        else:
            conversion = self.create_conversion(wallet_pair_id=wallet_pair_id, deposit_amount=deposit_amount)
        return conversion
