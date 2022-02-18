from enum import Enum


class ConversionStatus(Enum):
    USER_INITIATED = "USER_INITIATED"
    PROCESSING = "PROCESSING"
    WAITING_FOR_CLAIM = "WAITING_FOR_CLAIM"
    SUCCESS = "SUCCESS"


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
    TOKEN_UNLOCKED = "TOKEN_UNLOCKED"
    TOKEN_MINT_AND_TRANSFER = "TOKEN_MINT_AND_TRANSFER"
    TOKEN_LOCKED = "TOKEN_LOCKED"


EthereumToCardanoEvent = {"ethereum": [TransactionOperation.TOKEN_LOCKED.value],
                          "cardano": [TransactionOperation.TOKEN_MINT_AND_TRANSFER.value]}

CardanoToEthereumEvent = {
    "cardano": [TransactionOperation.TOKEN_RECEIVED.value, TransactionOperation.TOKEN_BURNT.value],
    "ethereum": [TransactionOperation.TOKEN_UNLOCKED.value]}


class TransactionStatus(Enum):
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    SUCCESS = "SUCCESS"


ALLOWED_CONVERTER_BRIDGE_TX_OPERATIONS = [TransactionOperation.TOKEN_BURNT.value,
                                          TransactionOperation.TOKEN_MINT_AND_TRANSFER.value,
                                          TransactionOperation.TOKEN_UNLOCKED.value]
