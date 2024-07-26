from enum import Enum


class ErrorCode(Enum):
    MISSING_BODY = "E0001"
    EMPTY_SCHEMA_FILE = "E0002"
    SCHEMA_NOT_MATCHING = "E0003"
    UNEXPECTED_ERROR_SCHEMA_VALIDATION = "E0004"
    PROPERTY_VALUES_EMPTY = "E0005"
    INCORRECT_SIGNATURE = "E0006"
    ALLOWED_DECIMAL_LIMIT_EXISTS = "E0007"
    INVALID_CONVERSION_ID = "E0008"
    EXISTING_TRANSACTION_IS_NOT_SUCCEEDED = "E0009"
    UNSUPPORTED_CHAIN_ID = "E0010"
    TRANSACTION_HASH_NOT_FOUND = "E0011"
    BLOCKCHAIN_TRANSACTION_NOT_MATCHING_CONVERSION = "E0012"
    RANDOM_TRANSACTION_HASH = "E0013"
    TRANSACTION_ALREADY_CREATED = "E0014"
    TRANSACTION_IS_NOT_READY_FOR_CLAIM = "E0015"
    INVALID_CARDANO_ADDRESS = "E0016"
    UNEXPECTED_ERROR_CARDANO_ADDRESS_VALIDATION = "E0017"
    UNEXPECTED_ERROR_ETHEREUM_TRANSACTION_DETAILS = "E0018"
    CONSUMER_EVENT_EMPTY = "E0019"
    UNSUPPORTED_BLOCKCHAIN_ON_SYSTEM = "E0020"
    UNHANDLED_BLOCKCHAIN_OPERATION = "E0021"
    UNEXPECTED_EVENT_TYPE = "E0022"
    MISSING_ETHEREUM_EVENT_FIELDS = "E0023"
    MISMATCH_AMOUNT = "E0024"
    TRANSACTION_ALREADY_PROCESSED = "E0025"
    MISSING_CARDANO_EVENT_FIELDS = "E0026"
    WALLET_PAIR_NOT_EXISTS = "E0027"
    BAD_REQUEST_ON_TRANSACTION_CREATION = "E0028"
    UNEXPECTED_ERROR_TRANSACTION_CREATION = "E0029"
    MISSING_CONVERTER_BRIDGE_FIELDS = "E0030"
    ACTIVITY_EVENT_NOT_MATCHING = "E0031"
    TRANSACTION_NOT_FOUND = "E0032"
    TRANSACTION_ALREADY_CONFIRMED = "E0033"
    UNEXPECTED_ERROR_ON_BLOCK_CONFIRMATION = "E0034"
    NOT_ENOUGH_BLOCK_CONFIRMATIONS = "E0035"
    NO_TRANSACTIONS_AVAILABLE = "E0036"
    TRANSACTION_WRONGLY_CREATED = "E0037"
    INVALID_TRANSACTION_OPERATION_PROVIDED = "E0038"
    TOPIC_NOT_FOUND = "E0039"
    UNABLE_TO_PARSE_THE_INPUT_EVENT = "E0040"
    QUEUE_DETAILS_NOT_FOUND = "E0041"
    INVALID_TRANSACTION_OPERATION = "E0042"
    LAMBDA_ARN_MINT_NOT_FOUND = "E0043"
    LAMBDA_ARN_BURN_NOT_FOUND = "E0044"
    SECRET_KEY_NOT_FOUND = "E0045"
    SECRET_DETAILS_FOR_CONTRACT_NOT_AVAILABLE = "E0046"
    INVALID_SIGNATURE_TYPE_PROVIDED = "E0047"
    SIGNING_SIGNATURE_FIELDS_EMPTY = "E0048"
    REQUIRED_SIGNING_ENVIRONMENT_FIELDS_NOT_FOUND = "E0049"
    UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL = "E0050"
    UNEXPECTED_ERROR_ON_SENDING_MESSAGE = "E0051"
    CONVERSION_NOT_READY_FOR_CLAIM = "E0052"
    INVALID_CLAIM_OPERATION_ON_BLOCKCHAIN = 'E0053'
    CONVERSION_ALREADY_CLAIMED = "E0054"
    INCORRECT_SIGNATURE_LENGTH = "E0055"
    UNEXPECTED_ERROR_ON_CLAIM_SIGNATURE_VALIDATION = "E0056"
    DERIVED_ADDRESS_NOT_FOUND = "E0057"
    TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API = "E0058"
    INVALID_ETHEREUM_ADDRESS = "E0059"
    DATA_NOT_AVAILABLE_ON_DERIVED_ADDRESS = "E0060"
    AMOUNT_LESS_THAN_MIN_VALUE = "E0061"
    AMOUNT_GREATER_THAN_MAX_VALUE = "E0062"
    CONVERSION_AMOUNT_CANT_BE_ZERO = "E0063"
    DAPP_AUTHORIZED_FOR_CARDANO_TX_UPDATE = "E0064"
    INVALID_CONVERSION_AMOUNT_PROVIDED = "E0065"
    MISMATCH_TOKEN_HOLDER = "E0066"
    UNABLE_TO_FIND_EVENTS_FOR_HASH = "E0067"
    CONVERSION_ALREADY_DONE = "E0068"
    TOKEN_CONTRACT_ADDRESS_EMPTY = "E0069"
    SIGNATURE_EXPIRED = "E0070"
    TOKEN_PAIR_NOT_EXISTS = "E0071"
    PAGE_SIZE_EXCEEDS_LIMIT = "E0072"
    INVALID_ASSET_TRANSFERRED = "E0073"
    UNEXPECTED_ERROR_ON_TX_HASH_PRESENCE = "E0074"
    INVALID_CONVERSION_DIRECTION = "E0075"
    CONVERSION_FEE_NOT_ALLOWED = "E0076"
    FUNCTION_NOT_FOUND_IN_ABI = "E0077"
    NOT_LIQUID_CONTRACT = "E0078"
    INSUFFICIENT_CONTRACT_LIQUIDITY = "E0079"
    INVALID_TOKEN_DATA = "E0080"
    BLOCKCHAIN_EVENT_DATA_DOES_NOT_MATCH_DATABASE_DATA = "E0082"


class ErrorDetails(Enum):
    E0001 = "Missing body"
    E0002 = "Schema is Empty"
    E0003 = "Schema is not matching with request"
    E0004 = "Unexpected error occurred during schema validation"
    E0005 = "Property value is empty"
    E0006 = "Incorrect signature provided"
    E0007 = "Allowed decimal limit exists"
    E0008 = "Invalid conversion id provided"
    E0009 = "You can't submit a transaction until the existing transaction get succeed"
    E0010 = "Unsupported chain id configured"
    E0011 = "Transaction hash is not found on the blockchain"
    E0012 = "Blockchain transaction details not matching with conversion request details"
    E0013 = "Transaction hash should be hex string with proper format"
    E0014 = "Transaction has been created already"
    E0015 = "Transaction is not ready for claiming"
    E0016 = "Invalid address for this network or malformed address format."
    E0017 = "Unexpected error occurred during address validation"
    E0018 = "Unexpected error occurred while getting ethereum transaction details"
    E0019 = "Missing required inputs "
    E0020 = "Unsupported blockchain provided to the system"
    E0021 = "Unhandled blockchain operation received"
    E0022 = "Unexpected event type received"
    E0023 = "Missing ethereum event required fields"
    E0024 = "Mismatch amount from request and contract event"
    E0025 = "Transaction already processed"
    E0026 = "Missing cardano event required fields"
    E0027 = "Wallet Pair not exists"
    E0028 = "Bad request received on the transaction"
    E0029 = "Unexpected error occurred while creation the transaction"
    E0030 = "Missing converter bridge fields"
    E0031 = "Activity event not matching"
    E0032 = "Transaction not found"
    E0033 = "Transaction already confirmed"
    E0034 = "Unexpected error occurred while confirming the blocks"
    E0035 = "Not enough block confirmation on the transaction"
    E0036 = "No transactions available for this conversion"
    E0037 = "Transaction wrongly created"
    E0038 = "Invalid transaction operation provided"
    E0039 = "Topic not found in the config"
    E0040 = "Unable to parse the input event provided"
    E0041 = "Queue details not found"
    E0042 = "Invalid Transaction Operation provided"
    E0043 = "Config of lambda arn for minting is empty"
    E0044 = "Config of lambda arn for burn is empty"
    E0045 = "Secret key not found for signing"
    E0046 = "Secret details for this contract not available"
    E0047 = "Invalid signature type provided"
    E0048 = "Signing signature fields is empty"
    E0049 = "Required environment variables not found on signing"
    E0050 = "Unexpected error occurred when calling the cardano service"
    E0051 = "Unexpected error occurred while sending the message to queue"
    E0052 = "Conversion is not ready for claim"
    E0053 = "Invalid claim operation for the blockchain"
    E0054 = "Conversion had been claimed already"
    E0055 = "Incorrect signature value or length provided"
    E0056 = "Unexpected error occurred while validating the claim signature"
    E0057 = "Derived address not found"
    E0058 = "Transaction Id not present in the cardano service api response"
    E0059 = "Invalid ethereum address provided"
    E0060 = "Data not available in the cardano derived address response"
    E0061 = "Amount is less than expected min value "
    E0062 = "Amount is greater than expected max value"
    E0063 = "Conversion amount must be greater tha zero"
    E0064 = "Not authorized to update the cardano transaction hash"
    E0065 = "Invalid conversion amount provided"
    E0066 = "Token holder address is mismatched from blockchain and conversion request"
    E0067 = "Unable to find any events for the given hash"
    E0068 = "Conversion has already been completed"
    E0069 = "Token contract address is empty"
    E0070 = "Signature expired for the given request"
    E0071 = "Token pair not exists"
    E0072 = "Page size exceeds the max limit"
    E0073 = "Invalid asset transferred to the deposit address"
    E0074 = "Unexpected error happened while checking the tx hash presence in the blockchain"
    E0075 = "Invalid value of conversion direction"
    E0076 = "Conversion fee not allowed for this type of conversions"
    E0077 = "The function 'getConverterBalance' was not found in this contract's abi."
    E0078 = "Contract is not liquid"
    E0079 = "Bridge contract liquidity is insufficient! At the moment conversion unavailable. Try again later."
    E0080 = "Invalid token data provided"
    E0082 = "Data from the blockchain_event does not match the transaction or conversion data from the DB"
