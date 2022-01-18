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
