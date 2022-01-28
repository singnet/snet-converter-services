from enum import Enum


class BlockchainEntities(Enum):
    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"
    SYMBOL = "symbol"
    LOGO = "logo"
    CHAIN_ID = "chain_id"
    BLOCK_CONFIRMATION = "block_confirmation"
    IS_EXTENSION_AVAILABLE = "is_extension_available"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TokenEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"
    SYMBOL = "symbol"
    LOGO = "logo"
    ALLOWED_DECIMAL = "allowed_decimal"
    BLOCKCHAIN = "blockchain"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TokenPairEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    CONTRACT_ADDRESS = "contract_address"
    FROM_TOKEN = "from_token"
    TO_TOKEN = "to_token"
    CONVERSION_FEE = "conversion_fee"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class ConversionFeeEntities(Enum):
    ID = "id"
    PERCENTAGE_FROM_SOURCE = "percentage_from_source"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class SignatureMetadataEntities(Enum):
    TOKEN_PAIR_ID = "token_pair_id"
    FROM_ADDRESS = "from_address"
    TO_ADDRESS = "to_address"
    AMOUNT = "amount"
    BLOCK_NUMBER = "block_number"


class WalletPairEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    TOKEN_PAIR_ID = "token_pair_id"
    FROM_ADDRESS = "from_address"
    TO_ADDRESS = "to_address"
    DEPOSIT_ADDRESS = "deposit_address"
    SIGNATURE = "signature"
    SIGNATURE_METADATA = "signature_metadata"
    SIGNATURE_EXPIRY = "signature_expiry"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class ConversionEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    WALLET_PAIR_ID = "wallet_pair_id"
    DEPOSIT_AMOUNT = "deposit_amount"
    CLAIM_AMOUNT = "claim_amount"
    FEE_AMOUNT = "fee_amount"
    STATUS = "status"
    CLAIM_SIGNATURE = "claim_signature"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class ConversionDetailEntities(Enum):
    CONVERSION = "conversion"
    WALLET_PAIR = "wallet_pair"
    FROM_TOKEN = "from_token"
    TO_TOKEN = "to_token"
    TRANSACTION = "transaction"


class TransactionConversionEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    CONVERSION_ID = "conversion_id"
    STATUS = "status"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TransactionEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    CONVERSION_TRANSACTION_ID = "transaction_conversion_id"
    FROM_TOKEN_ID = "from_token_id"
    TO_TOKEN_ID = "to_token_id"
    TRANSACTION_VISIBILITY = "transaction_visibility"
    TRANSACTION_OPERATION = "transaction_operation"
    TRANSACTION_HASH = "transaction_hash"
    TRANSACTION_AMOUNT = "transaction_amount"
    STATUS = "status"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TransactionDetailEntities(Enum):
    CONVERSION_ID = "conversion_id"
    TRANSACTIONS = "transactions"


class PaginationEntity(Enum):
    ITEMS = "items"
    ITEM = "item"
    META = "meta"
    PAGE_SIZE = "page_size"
    PAGE_NUMBER = "page_number"
    OFFSET = "offset"
    LIMIT = "limit"
    TOTAL_RECORDS = "total_records"
    PAGE_COUNT = "page_count"