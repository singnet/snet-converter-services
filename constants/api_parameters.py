from enum import Enum


class ApiParameters(Enum):
    TOKEN_PAIR_ID = "token_pair_id"
    AMOUNT = "amount"
    FROM_ADDRESS = "from_address"
    TO_ADDRESS = "to_address"
    BLOCK_NUMBER = "block_number"
    SIGNATURE = "signature"
    KEY = "key"
    CONVERSION_ID = "conversion_id"
    TRANSACTION_HASH = "transaction_hash"
    PAGE_SIZE = "page_size"
    PAGE_NUMBER = "page_number"
    ADDRESS = "address"
    ETHEREUM_ADDRESS = "ethereum_address"


