from enum import Enum

MAX_ALLOWED_DECIMAL = 20


class BlockchainName(Enum):
    ETHEREUM = "Ethereum"
    CARDANO = "Cardano"


class CreatedBy(Enum):
    DAPP = "DApp"
    BACKEND = "Backend"


class ConversionOn(Enum):
    FROM = "from"
    TO = "to"


class TopicName(Enum):
    pass


class QueueName(Enum):
    CONVERTER_BRIDGE = "CONVERTER_BRIDGE"
    CONVERTER_BRIDGE_1 = "CONVERTER_BRIDGE_1"
    CONVERTER_BRIDGE_2 = "CONVERTER_BRIDGE_2"
    CONVERTER_BRIDGE_3 = "CONVERTER_BRIDGE_3"
    CONVERTER_BRIDGE_4 = "CONVERTER_BRIDGE_4"
    EVENT_CONSUMER = "EVENT_CONSUMER"


class SignatureTypeEntities(Enum):
    CONVERSION_IN = "__conversionIn"
    CONVERSION_OUT = "__conversionOut"


class MaxRetryEntities(Enum):
    BLOCK_CONFIRMATION = "BLOCK_CONFIRMATION"
    TRANSACTION_HASH_PRESENCE = "TRANSACTION_HASH_PRESENCE"


class SleepTimeEntities(Enum):
    BLOCK_CONFIRMATION = "BLOCK_CONFIRMATION"
    TRANSACTION_HASH_PRESENCE = "TRANSACTION_HASH_PRESENCE"


SIGNATURE_TYPES = [SignatureTypeEntities.CONVERSION_IN.value, SignatureTypeEntities.CONVERSION_OUT.value]

ENV_CONVERTER_SIGNER_PRIVATE_KEY_PATH = "CONVERTER_SIGNER_PRIVATE_KEY_PATH"

ETHEREUM_WALLET_ADDRESS_LENGTH = 42
MAX_PAGE_SIZE = 20
