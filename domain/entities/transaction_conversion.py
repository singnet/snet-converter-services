from datetime import date

from constants.entity import TransactionConversionEntities
from utils.general import datetime_to_str


class ConversionTransaction:

    def __init__(self, row_id: int, id: str, conversion_id: int, status: str, created_by: str, created_at: date,
                 updated_at: date):
        self.row_id = row_id
        self.id = id
        self.conversion_id = conversion_id
        self.status = status
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        return {
            TransactionConversionEntities.ROW_ID.value: self.row_id,
            TransactionConversionEntities.ID.value: self.id,
            TransactionConversionEntities.CONVERSION_ID.value: self.conversion_id,
            TransactionConversionEntities.STATUS.value: self.status,
            TransactionConversionEntities.CREATED_BY.value: self.created_by,
            TransactionConversionEntities.CREATED_AT.value: self.created_at,
            TransactionConversionEntities.UPDATED_AT.value: self.updated_at,
        }
