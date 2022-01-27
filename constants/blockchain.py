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
