from datetime import date

from constants.entity import TokenPairEntities
from domain.entities.conversion_fee import ConversionFee
from domain.entities.token import Token
from utils.general import datetime_to_str
from decimal import Decimal


class TokenPair:

    def __init__(self, row_id: int, id_: str, min_value: Decimal, max_value: Decimal, created_by: str, created_at: date,
                 updated_at: date, from_token_obj: Token, to_token_obj: Token, conversion_fee_obj: ConversionFee,
                 conversion_ratio: Decimal, is_liquid: bool):
        self.row_id = row_id
        self.id = id_
        self.min_value = str(min_value.normalize())
        self.max_value = str(max_value.normalize())
        self.created_by = created_by
        self.from_token_obj = from_token_obj
        self.to_token_obj = to_token_obj
        self.conversion_fee_obj = conversion_fee_obj
        self.conversion_ratio = str(conversion_ratio) if conversion_ratio else None
        self.is_liquid = is_liquid
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        from_token = {} if self.from_token_obj is None else self.from_token_obj.to_dict()
        to_token = {} if self.to_token_obj is None else self.to_token_obj.to_dict()
        conversion_fee = {} if self.conversion_fee_obj is None else self.conversion_fee_obj.to_dict()

        return {
            TokenPairEntities.ROW_ID.value: self.row_id,
            TokenPairEntities.ID.value: self.id,
            TokenPairEntities.MIN_VALUE.value: self.min_value,
            TokenPairEntities.MAX_VALUE.value: self.max_value,
            TokenPairEntities.FROM_TOKEN.value: from_token,
            TokenPairEntities.TO_TOKEN.value: to_token,
            TokenPairEntities.CONVERSION_FEE.value: conversion_fee,
            TokenPairEntities.CONVERSION_RATIO.value: self.conversion_ratio,
            TokenPairEntities.IS_LIQUID.value: self.is_liquid,
            TokenPairEntities.CREATED_BY.value: self.created_by,
            TokenPairEntities.CREATED_AT.value: self.created_at,
            TokenPairEntities.UPDATED_AT.value: self.updated_at
        }
