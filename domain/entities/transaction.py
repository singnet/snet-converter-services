from datetime import date
from decimal import Decimal

from constants.entity import TransactionEntities
from domain.entities.token import Token
from domain.entities.transaction_conversion import ConversionTransaction
from utils.general import datetime_to_str


class Transaction:
    def __init__(self, row_id: int, id: str, conversion_transaction_id: int, token_id: int,
                 transaction_visibility: str, transaction_operation: str, transaction_hash: str,
                 transaction_amount: Decimal, confirmation: int, status: str, created_by: str, created_at: date,
                 updated_at: date, conversion_transaction_obj: ConversionTransaction, token_obj: Token):
        self.row_id = row_id
        self.id = id
        self.conversion_transaction_id = conversion_transaction_id
        self.token_id = token_id
        self.transaction_visibility = transaction_visibility
        self.transaction_operation = transaction_operation
        self.transaction_hash = transaction_hash
        self.transaction_amount = str(transaction_amount.normalize())
        self.confirmation = confirmation
        self.status = status
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)
        self.conversion_transaction_obj = conversion_transaction_obj
        self.token_obj = token_obj

    def to_dict(self):
        conversion_transaction = {} if self.conversion_transaction_obj is None else self.conversion_transaction_obj.to_dict()
        token = {} if self.token_obj is None else self.token_obj.to_dict()

        return {
            TransactionEntities.ROW_ID.value: self.row_id,
            TransactionEntities.ID.value: self.id,
            TransactionEntities.CONVERSION_TRANSACTION_ID.value: self.conversion_transaction_id,
            TransactionEntities.TOKEN_ID.value: self.token_id,
            TransactionEntities.TRANSACTION_VISIBILITY.value: self.transaction_visibility,
            TransactionEntities.TRANSACTION_OPERATION.value: self.transaction_operation,
            TransactionEntities.TRANSACTION_HASH.value: self.transaction_hash,
            TransactionEntities.TRANSACTION_AMOUNT.value: self.transaction_amount,
            TransactionEntities.CONFIRMATION.value: self.confirmation,
            TransactionEntities.STATUS.value: self.status,
            TransactionEntities.CREATED_BY.value: self.created_by,
            TransactionEntities.CREATED_AT.value: self.created_at,
            TransactionEntities.UPDATED_AT.value: self.updated_at,
            TransactionEntities.CONVERSION_TRANSACTION.value: conversion_transaction,
            TransactionEntities.TOKEN.value: token
        }
