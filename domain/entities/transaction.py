from datetime import date
from decimal import Decimal

from constants.entity import TransactionEntities
from utils.general import datetime_to_str


class Transaction:
    def __init__(self, row_id: int, id: str, conversion_transaction_id: int, from_token_id: int, to_token_id: int,
                 transaction_visibility: str, transaction_operation: str, transaction_hash: str,
                 transaction_amount: Decimal, status: str, created_by: str, created_at: date, updated_at: date):
        self.row_id = row_id
        self.id = id
        self.conversion_transaction_id = conversion_transaction_id
        self.from_token_id = from_token_id
        self.to_token_id = to_token_id
        self.transaction_visibility = transaction_visibility
        self.transaction_operation = transaction_operation
        self.transaction_hash = transaction_hash
        self.transaction_amount = str(transaction_amount.normalize())
        self.status = status
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        return {
            TransactionEntities.ROW_ID.value: self.row_id,
            TransactionEntities.ID.value: self.id,
            TransactionEntities.CONVERSION_TRANSACTION_ID.value: self.conversion_transaction_id,
            TransactionEntities.FROM_TOKEN_ID.value: self.from_token_id,
            TransactionEntities.TO_TOKEN_ID.value: self.to_token_id,
            TransactionEntities.TRANSACTION_VISIBILITY.value: self.transaction_visibility,
            TransactionEntities.TRANSACTION_OPERATION.value: self.transaction_operation,
            TransactionEntities.TRANSACTION_HASH.value: self.transaction_hash,
            TransactionEntities.TRANSACTION_AMOUNT.value: self.transaction_amount,
            TransactionEntities.STATUS.value: self.status,
            TransactionEntities.CREATED_BY.value: self.created_by,
            TransactionEntities.CREATED_AT.value: self.created_at,
            TransactionEntities.UPDATED_AT.value: self.updated_at
        }
