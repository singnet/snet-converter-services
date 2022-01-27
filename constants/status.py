from enum import Enum


class ConversionStatus(Enum):
    USER_INITIATED = "USER_INITIATED"
    PROCESSING = "PROCESSING"


class ConversionTransactionStatus(Enum):
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    PROCESSING = "PROCESSING"


class TransactionVisibility(Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


class TransactionOperation(Enum):
    TOKEN_RECEIVED = "TOKEN_RECEIVED"
    TOKEN_CLAIMED = "TOKEN_CLAIMED"


class TransactionStatus(Enum):
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    SUCCESS = "SUCCESS"
