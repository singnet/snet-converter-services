from enum import Enum


class ConversionStatus(Enum):
    USER_INITIATED = "USER_INITIATED"
    PROCESSING = "PROCESSING"
    WAITING_FOR_CLAIM = "WAITING_FOR_CLAIM"
    SUCCESS = "SUCCESS"
    CLAIM_INITIATED = "CLAIM_INITIATED"
    EXPIRED = "EXPIRED"


class ConversionTransactionStatus(Enum):
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    PROCESSING = "PROCESSING"


class TransactionVisibility(Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


class TransactionOperation(Enum):
    TOKEN_RECEIVED = "TOKEN_RECEIVED"
    TOKEN_BURNT = "TOKEN_BURNT"
    TOKEN_MINTED = "TOKEN_MINTED"
    TOKEN_TRANSFERRED = "TOKEN_TRANSFERRED"


EthereumToCardanoEvent = {"ethereum": [TransactionOperation.TOKEN_BURNT.value],
                          "cardano": [TransactionOperation.TOKEN_MINTED.value]}

CardanoToEthereumEvent = {
    "cardano": [TransactionOperation.TOKEN_RECEIVED.value, TransactionOperation.TOKEN_BURNT.value],
    "ethereum": [TransactionOperation.TOKEN_MINTED.value]}

EthereumToBinanceEvent = {"ethereum": [TransactionOperation.TOKEN_BURNT.value],
                          "binance": [TransactionOperation.TOKEN_MINTED.value]}

BinanceToEthereumEvent = {"binance": [TransactionOperation.TOKEN_BURNT.value],
                          "ethereum": [TransactionOperation.TOKEN_MINTED.value]}

CardanoToCardanoEvent = {"cardano": [TransactionOperation.TOKEN_RECEIVED.value, TransactionOperation.TOKEN_BURNT.value],
                         "cardano_": [TransactionOperation.TOKEN_TRANSFERRED.value]}


class TransactionStatus(Enum):
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    SUCCESS = "SUCCESS"


ALLOWED_CONVERTER_BRIDGE_TX_OPERATIONS = [TransactionOperation.TOKEN_BURNT.value,
                                          TransactionOperation.TOKEN_MINTED.value]
