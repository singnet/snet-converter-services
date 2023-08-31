from enum import Enum


class EthereumNetwork(Enum):
    MAINNET = 1
    ROPSTEN = 3
    KOVAN = 42
    GOERLI = 5
    SEPOLIA = 11155111


class EthereumEnvironment(Enum):
    MAINNET = "production"
    ROPSTEN = "test"
    KOVAN = "test"
    GOERLI = "test"
    SEPOLIA = "test"


class BinanceNetwork(Enum):
    MAINNET = 56
    TESTNET = 97


class BinanceEnvironment(Enum):
    MAINNET = "production"
    TESTNET = "test"


class CardanoNetwork(Enum):
    MAINNET = 1
    TESTNET = 2
    PREPROD = 0


class CardanoEnvironment(Enum):
    MAINNET = "production"
    TESTNET = "test"
    PREPROD = "test"


EthereumSupportedNetwork = [EthereumNetwork.MAINNET.value, EthereumNetwork.ROPSTEN.value, EthereumNetwork.KOVAN.value,
                            EthereumNetwork.GOERLI.value, EthereumNetwork.SEPOLIA.value]

BinanceSupportedNetwork = [BinanceNetwork.MAINNET.value, BinanceNetwork.TESTNET.value]

CardanoSupportedNetwork = [CardanoNetwork.MAINNET.value, CardanoNetwork.TESTNET.value, CardanoNetwork.PREPROD.value]


class CardanoTransactionEntities(Enum):
    FEES = "fees"
    INDEX = "index"
    ASSET_MINT_OR_BURN_COUNT = "asset_mint_or_burn_count"
    BLOCK_HEIGHT = "block_height"
    BLOCK_TIME = "block_time"


class EthereumBlockchainEntities(Enum):
    BLOCK_NUMBER = "blockNumber"


class BinanceBlockchainEntities(Enum):
    BLOCK_NUMBER = "blockNumber"


class CardanoBlockEntities(Enum):
    CONFIRMATIONS = "confirmations"
