from datetime import date
from decimal import Decimal

from constants.entity import ConversionFeeEntities
from utils.general import datetime_to_str


class ConversionFee:

    def __init__(self, id: str, percentage_from_source: Decimal, created_by: str, created_at: date, updated_at: date):
        self.id = id
        self.percentage_from_source = str(percentage_from_source.normalize())
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        return {
            ConversionFeeEntities.ID.value: self.id,
            ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value: self.percentage_from_source,
            ConversionFeeEntities.CREATED_BY.value: self.created_by,
            ConversionFeeEntities.CREATED_AT.value: self.created_at,
            ConversionFeeEntities.UPDATED_AT.value: self.updated_at
        }
