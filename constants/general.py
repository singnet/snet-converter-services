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
