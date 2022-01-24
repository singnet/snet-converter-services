from enum import Enum

MAX_ALLOWED_DECIMAL = 20


class BlockchainName(Enum):
    ETHEREUM = "Ethereum"
    CARDANO = "Cardano"


class CreatedBy(Enum):
    DAPP = "DApp"
