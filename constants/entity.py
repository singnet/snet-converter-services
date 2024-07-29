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
    TOKEN_ADDRESS = "token_address"
    CONTRACT_ADDRESS = "contract_address"
    BLOCKCHAIN = "blockchain"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TokenPairEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    FROM_TOKEN = "from_token"
    TO_TOKEN = "to_token"
    CONVERSION_FEE = "conversion_fee"
    CONVERSION_RATIO = "conversion_ratio"
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
    SIGNATURE = "signature"


class WalletPairEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    TOKEN_PAIR_ID = "token_pair_id"
    FROM_ADDRESS = "from_address"
    TO_ADDRESS = "to_address"
    DEPOSIT_ADDRESS = "deposit_address"
    DEPOSIT_ADDRESS_DETAIL = "deposit_address_detail"
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
    TRANSACTIONS = "transactions"


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
    TOKEN_ID = "token_id"
    TRANSACTION_VISIBILITY = "transaction_visibility"
    TRANSACTION_OPERATION = "transaction_operation"
    TRANSACTION_HASH = "transaction_hash"
    TRANSACTION_AMOUNT = "transaction_amount"
    CONFIRMATION = "confirmation"
    STATUS = "status"
    CREATED_BY = "created_by"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    CONVERSION_TRANSACTION = "conversion_transaction"
    TOKEN = "token"


class MessagePoolEntities(Enum):
    ROW_ID = "row_id"
    ID = "id"
    NAME = "name"
    MESSAGE_GROUP_ID = "message_group_id"
    IS_ENABLED = "is_enabled"
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


class EventConsumerEntity(Enum):
    BLOCKCHAIN_NAME = "blockchain_name"
    BLOCKCHAIN_EVENT = "blockchain_event"


class CardanoEventConsumer(Enum):
    EVENT_TYPE = "event_type"
    TX_HASH = "tx_hash"
    ADDRESS = "address"
    TRANSACTION_DETAIL = "transaction_detail"
    TX_TYPE = "tx_type"
    CONFIRMATIONS = "confirmations"
    TX_AMOUNT = "tx_amount"
    RECORDS = "Records"
    BODY = "body"
    MESSAGE = "Message"
    ASSET = "asset"
    POLICY_ID = "policy_id"
    ASSET_NAME = "asset_name"


class ConverterBridgeEntities(Enum):
    BLOCKCHAIN_NAME = "blockchain_name"
    BLOCKCHAIN_EVENT = "blockchain_event"
    BLOCKCHAIN_NETWORK_ID = "blockchain_network_id"
    CONVERSION_ID = "conversion_id"
    TX_AMOUNT = "tx_amount"
    TX_OPERATION = "tx_operation"
    RECORDS = "Records"
    BODY = "body"
    MESSAGE = "message"


class CardanoEventType(Enum):
    TOKEN_RECEIVED = "TOKEN_RECEIVED"
    TOKEN_BURNT = "TOKEN_BURNT"
    TOKEN_MINTED = "TOKEN_MINTED"
    TOKEN_TRANSFERRED = "TOKEN_TRANSFERRED"


CardanoAllowedEventType = [CardanoEventType.TOKEN_RECEIVED.value, CardanoEventType.TOKEN_BURNT.value,
                           CardanoEventType.TOKEN_MINTED.value, CardanoEventType.TOKEN_TRANSFERRED.value]

CardanoServicesEventTypes = [CardanoEventType.TOKEN_BURNT.value, CardanoEventType.TOKEN_MINTED.value,
                             CardanoEventType.TOKEN_TRANSFERRED.value]


class EthereumEventConsumerEntities(Enum):
    CONVERSION_ID = "conversionId"
    TRANSACTION_HASH = "transaction_hash"
    NAME = "name"
    JSON_STR = "json_str"
    DATA = "data"
    TOKEN_HOLDER = "tokenHolder"
    AMOUNT = "amount"
    ARGS = "args"


class EthereumEventType(Enum):
    TOKEN_BURNT = "ConversionOut"
    TOKEN_MINTED = "ConversionIn"


EthereumAllowedEventType = [EthereumEventType.TOKEN_BURNT.value, EthereumEventType.TOKEN_MINTED.value]


class BinanceEventConsumerEntities(Enum):
    CONVERSION_ID = "conversionId"
    TRANSACTION_HASH = "transaction_hash"
    NAME = "name"
    JSON_STR = "json_str"
    DATA = "data"
    TOKEN_HOLDER = "tokenHolder"
    AMOUNT = "amount"
    ARGS = "args"


class BinanceEventType(Enum):
    TOKEN_BURNT = "ConversionOut"
    TOKEN_MINTED = "ConversionIn"


BinanceAllowedEventType = [BinanceEventType.TOKEN_BURNT.value, BinanceEventType.TOKEN_MINTED.value]


class CardanoAPIEntities(Enum):
    HASH = "hash"
    PATH_PARAMETERS = "pathParameters"
    TOKEN = "token"
    BODY = "body"
    ENVIRONMENT = "environment"
    CARDANO_ADDRESS = "cardano_address"
    AMOUNT = "amount"
    TRANSACTION_DETAILS = "transaction_details"
    SOURCE_ADDRESS = "source_address"
    TRANSACTION_ID = "transaction_id"
    DERIVED_ADDRESS = "derived_address"
    DEPOSIT_ADDRESS_DETAILS = "deposit_address_details"
    ADDRESS = "address"
    INDEX = "index"
    ROLE = "role"
    DATA = "data"
    CONVERSION_ID = "conversion_id"
    FEE = "fee"
    DECIMALS_DIFFERENCE = "decimals_difference"
    CONVERSION_RATIO = "conversion_ratio"
    BURNT_TOKEN = "burnt_token"


class WalletPairResponseEntities(Enum):
    ADDRESSES = "addresses"
    CARDANO_ADDRESS = "cardano_address"


class SQSEntities(Enum):
    QUEUE_URL = "QueueUrl"
    MESSAGE_BODY = "MessageBody"
    MESSAGE_GROUP_ID = "MessageGroupId"


class ConversionReportingEntities(Enum):
    FROM_BLOCKCHAIN = "from_blockchain"
    TO_BLOCKCHAIN = "to_blockchain"
    TOKEN = "token"
    TOTAL_CONVERSION = "total_conversion"
    EACH_CONVERSION = "each_conversion"
    AMOUNT = "amount"
    STATUS = "status"
    COUNT = "count"
