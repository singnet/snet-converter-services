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


class SignatureTypeEntities(Enum):
    CONVERSION_IN = "__conversionIn"
    CONVERSION_OUT = "__conversionOut"


SIGNATURE_TYPES = [SignatureTypeEntities.CONVERSION_IN.value, SignatureTypeEntities.CONVERSION_OUT.value]

ENV_CONVERTER_SIGNER_PRIVATE_KEY_PATH = "CONVERTER_SIGNER_PRIVATE_KEY_PATH"
