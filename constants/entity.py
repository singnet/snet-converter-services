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
