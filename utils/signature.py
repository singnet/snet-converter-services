import web3
from eth_account.messages import defunct_hash_message
from web3 import Web3

from common.logger import get_logger
from config import NETWORK
from constants.entity import SignatureMetadataEntities
from utils.general import get_ethereum_network_url

logger = get_logger(__name__)


def validate_conversion_signature(token_pair_id, amount, from_address, to_address, block_number, signature,
                                  is_signer_as_from_address, chain_id):
    logger.info("Validating the signature")
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


def create_signature_metadata(token_pair_id, amount, from_address, to_address, block_number):
    return {
        SignatureMetadataEntities.TOKEN_PAIR_ID.value: token_pair_id,
        SignatureMetadataEntities.FROM_ADDRESS.value: from_address,
        SignatureMetadataEntities.TO_ADDRESS.value: to_address,
        SignatureMetadataEntities.AMOUNT.value: amount,
        SignatureMetadataEntities.BLOCK_NUMBER.value: int(block_number),
    }
