import math
from decimal import Decimal

from common.logger import get_logger
from config import CARDANO_DEPOSIT_ADDRESS
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName, MAX_ALLOWED_DECIMAL
from utils.exceptions import InternalServerErrorException

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


def validate_address(from_address, to_address, from_blockchain_name, to_blockchain_name):
    logger.info(f"validating the input address from_address={from_address}, from_blockchain_name={from_blockchain_name}"
                f", to_adress={to_address}, to_blockchain_name={to_blockchain_name}")
    pass


def get_lowest_unit_amount(amount, allowed_decimal):
    if allowed_decimal is None or allowed_decimal <= 0:
        return amount

    if allowed_decimal > MAX_ALLOWED_DECIMAL:
        raise InternalServerErrorException(error_code=ErrorCode.ALLOWED_DECIMAL_LIMIT_EXISTS.value,
                                           error_details=ErrorDetails[ErrorCode.ALLOWED_DECIMAL_LIMIT_EXISTS.value].value)
    return amount * Decimal(math.pow(10, allowed_decimal))
