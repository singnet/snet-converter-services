from datetime import date
from decimal import Decimal

from constants.entity import ConversionFeeEntities
from domain.entities.token import Token
from utils.general import datetime_to_str


class ConversionFee:

    def __init__(self, id: str, percentage_from_source: Decimal, token_obj: Token, created_by: str, created_at: date, updated_at: date):
        self.id = id
        self.percentage_from_source = str(percentage_from_source.normalize())
        self.token_obj = token_obj
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        token_obj = {} if self.token_obj is None else self.token_obj.to_dict()
        return {
            ConversionFeeEntities.ID.value: self.id,
            ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value: self.percentage_from_source,
            ConversionFeeEntities.TOKEN.value: token_obj,
            ConversionFeeEntities.CREATED_BY.value: self.created_by,
            ConversionFeeEntities.CREATED_AT.value: self.created_at,
            ConversionFeeEntities.UPDATED_AT.value: self.updated_at
        }
