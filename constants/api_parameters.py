from enum import Enum


class ApiParameters(Enum):
    BLOCKCHAIN_NAME = "blockchain_name"
    TOKEN_SYMBOL = "token_symbol"
    TOKEN_PAIR_ID = "token_pair_id"
    AMOUNT = "amount"
    FROM_ADDRESS = "from_address"
    TO_ADDRESS = "to_address"
    BLOCK_NUMBER = "block_number"
    SIGNATURE = "signature"
    KEY = "key"
    CONVERSION_ID = "conversion_id"
    CONVERSION_STATUS = "conversion_status"
    TRANSACTION_HASH = "transaction_hash"
    PAGE_SIZE = "page_size"
    PAGE_NUMBER = "page_number"
    ORDER_BY = "order_by"
    ADDRESS = "address"
    ETHEREUM_ADDRESS = "ethereum_address"


