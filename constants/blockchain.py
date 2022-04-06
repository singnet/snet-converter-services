from enum import Enum


class EthereumNetwork(Enum):
    MAINNET = 1
    ROPSTEN = 3
    KOVAN = 42


class EthereumEnvironment(Enum):
    MAINNET = "production"
    ROPSTEN = "test"
    KOVAN = "test"


class CardanoNetwork(Enum):
    MAINNET = 1
    TESTNET = 2


class CardanoEnvironment(Enum):
    MAINNET = "production"
    TESTNET = "test"


EthereumSupportedNetwork = [EthereumNetwork.MAINNET.value, EthereumNetwork.ROPSTEN.value, EthereumNetwork.KOVAN.value]

CardanoSupportedNetwork = [CardanoNetwork.MAINNET.value, CardanoNetwork.TESTNET.value]


class CardanoTransactionEntities(Enum):
    FEES = "fees"
    INDEX = "index"
    ASSET_MINT_OR_BURN_COUNT = "asset_mint_or_burn_count"
    BLOCK_HEIGHT = "block_height"
    BLOCK_TIME = "block_time"


class EthereumBlockchainEntities(Enum):
    BLOCK_NUMBER = "blockNumber"


class CardanoBlockEntities(Enum):
    CONFIRMATIONS = "confirmations"
