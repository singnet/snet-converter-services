import json
import os

import web3
from eth_account.messages import defunct_hash_message, encode_defunct
from eth_utils import ValidationError
from web3 import Web3

from common.boto_utils import BotoUtils
from common.logger import get_logger
from constants.entity import SignatureMetadataEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import SIGNATURE_TYPES, ENV_CONVERTER_SIGNER_PRIVATE_KEY_PATH
from utils.exceptions import InternalServerErrorException, BadRequestException
from utils.general import get_ethereum_network_url, string_to_bytes_to_hex, get_evm_network_url

logger = get_logger(__name__)


def validate_conversion_signature(token_pair_id, amount, from_address, to_address, block_number, signature,
                                  is_signer_as_from_address, chain_id):
    logger.info("Validating the conversion request signature")
    if is_signer_as_from_address:
        target_address = from_address
    else:
        target_address = to_address

    message = web3.Web3.soliditySha3(
        ["string", "string", "string", "string", "uint256"],
        [token_pair_id, amount, from_address, to_address, block_number],
    )

    hash_message = defunct_hash_message(message)
    web3_object = Web3(web3.providers.HTTPProvider(get_ethereum_network_url(chain_id=chain_id)))
    signer_address = web3_object.eth.account.recoverHash(
        message_hash=hash_message, signature=signature
    )

    return signer_address == target_address


def validate_conversion_claim_signature(conversion_id, amount, from_address, to_address, signature, chain_id):
    logger.info("Validating the signature")
    try:
        message = web3.Web3.soliditySha3(
            ["string", "string", "string", "string"],
            [conversion_id, amount, from_address, to_address],
        )

        hash_message = defunct_hash_message(message)
        web3_object = Web3(web3.providers.HTTPProvider(get_ethereum_network_url(chain_id=chain_id)))
        signer_address = web3_object.eth.account.recoverHash(
            message_hash=hash_message, signature=signature
        )
    except ValidationError as e:
        logger.info(e)
        raise BadRequestException(error_code=ErrorCode.INCORRECT_SIGNATURE_LENGTH.value,
                                  error_details=ErrorDetails[ErrorCode.INCORRECT_SIGNATURE_LENGTH.value].value)
    except Exception as e:
        logger.exception(e)
        raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CLAIM_SIGNATURE_VALIDATION.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNEXPECTED_ERROR_ON_CLAIM_SIGNATURE_VALIDATION.value].value)

    return signer_address == to_address


def create_signature_metadata(token_pair_id, amount, from_address, to_address, block_number):
    return {
        SignatureMetadataEntities.TOKEN_PAIR_ID.value: token_pair_id,
        SignatureMetadataEntities.FROM_ADDRESS.value: from_address,
        SignatureMetadataEntities.TO_ADDRESS.value: to_address,
        SignatureMetadataEntities.AMOUNT.value: amount,
        SignatureMetadataEntities.BLOCK_NUMBER.value: int(block_number),
    }


def generate_signature(signature_type, private_key, user_address, conversion_id, amount, contract_address, chain_id):
    if not signature_type or not private_key or not user_address or not conversion_id or not contract_address or \
            not amount:
        raise InternalServerErrorException(
            error_code=ErrorCode.SIGNING_SIGNATURE_FIELDS_EMPTY.value,
            error_details=ErrorDetails[ErrorCode.SIGNING_SIGNATURE_FIELDS_EMPTY.value].value)

    user_address = Web3.toChecksumAddress(user_address)
    contract_address = Web3.toChecksumAddress(contract_address)
    conversion_id_bytes = string_to_bytes_to_hex(conversion_id)

    message = web3.Web3.soliditySha3(
        ["string", "uint256", "address", "bytes32", "address"],
        [signature_type, int(amount), user_address, conversion_id_bytes, contract_address],
    )

    message_hash = encode_defunct(message)

    network_url = get_evm_network_url(chain_id=chain_id)
    web3_object = Web3(web3.providers.HTTPProvider(network_url))
    signed_message = web3_object.eth.account.sign_message(message_hash, private_key=private_key)

    return signed_message.signature.hex()


def get_signature(signature_type, user_address, conversion_id, amount, contract_address, chain_id):
    logger.info(f"Getting the signature for signature_type={signature_type}, user_address={user_address}, "
                f"conversion_id={conversion_id}, amount={amount}, contract_address={contract_address}, "
                f"chain_id={chain_id}")

    if signature_type not in SIGNATURE_TYPES:
        raise InternalServerErrorException(
            error_code=ErrorCode.INVALID_SIGNATURE_TYPE_PROVIDED.value,
            error_details=ErrorDetails[ErrorCode.INVALID_SIGNATURE_TYPE_PROVIDED.value].value)
    region_name = os.getenv('AWS_REGION', None)
    secret_name = os.getenv(ENV_CONVERTER_SIGNER_PRIVATE_KEY_PATH, None)
    if not region_name or not secret_name:
        raise InternalServerErrorException(
            error_code=ErrorCode.REQUIRED_SIGNING_ENVIRONMENT_FIELDS_NOT_FOUND.value,
            error_details=ErrorDetails[ErrorCode.REQUIRED_SIGNING_ENVIRONMENT_FIELDS_NOT_FOUND.value].value)

    boto_utils_obj = BotoUtils(region_name=region_name)
    secrets = boto_utils_obj.get_parameter_value_from_secrets_manager(secret_name=secret_name)

    if not secrets:
        raise InternalServerErrorException(error_code=ErrorCode.SECRET_KEY_NOT_FOUND.value,
                                           error_details=ErrorDetails[ErrorCode.SECRET_KEY_NOT_FOUND.value].value)
    private_key = json.loads(secrets).get(contract_address)

    if not private_key:
        raise InternalServerErrorException(
            error_code=ErrorCode.SECRET_DETAILS_FOR_CONTRACT_NOT_AVAILABLE.value,
            error_details=ErrorDetails[ErrorCode.SECRET_DETAILS_FOR_CONTRACT_NOT_AVAILABLE.value].value)

    return generate_signature(signature_type=signature_type, private_key=private_key, user_address=user_address,
                              conversion_id=conversion_id, amount=amount, contract_address=contract_address,
                              chain_id=chain_id)
