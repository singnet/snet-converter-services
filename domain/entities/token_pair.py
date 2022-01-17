from datetime import date

from constants.entity import TokenPairEntities
from domain.entities.conversion_fee import ConversionFee
from domain.entities.token import Token
from utils.general import datetime_to_str
from decimal import Decimal


class TokenPair:

    def __init__(self, id: str, min_value: Decimal, max_value: Decimal, contract_address: str,
                 created_by: str, created_at: date, updated_at: date, from_token_obj: Token, to_token_obj: Token,
                 conversion_fee_obj: ConversionFee):
        self.id = id
        self.min_value = str(min_value.normalize())
        self.max_value = str(max_value.normalize())
        self.contract_address = contract_address
        self.created_by = created_by
        self.from_token_obj = from_token_obj
        self.to_token_obj = to_token_obj
        self.conversion_fee_obj = conversion_fee_obj
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        from_token = {} if self.from_token_obj is None else self.from_token_obj.to_dict()
        to_token = {} if self.to_token_obj is None else self.to_token_obj.to_dict()
        conversion_fee = {} if self.conversion_fee_obj is None else self.conversion_fee_obj.to_dict()

        return {
            TokenPairEntities.ID.value: self.id,
            TokenPairEntities.MIN_VALUE.value: self.min_value,
            TokenPairEntities.MAX_VALUE.value: self.max_value,
            TokenPairEntities.CONTRACT_ADDRESS.value: self.contract_address,
            TokenPairEntities.FROM_TOKEN.value: from_token,
            TokenPairEntities.TO_TOKEN.value: to_token,
            TokenPairEntities.CONVERSION_FEE.value: conversion_fee,
            TokenPairEntities.CREATED_BY.value: self.created_by,
            TokenPairEntities.CREATED_AT.value: self.created_at,
            TokenPairEntities.UPDATED_AT.value: self.updated_at
        }
