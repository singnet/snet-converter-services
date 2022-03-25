from constants.entity import ConversionDetailEntities
from domain.entities.conversion import Conversion
from domain.entities.token import Token
from domain.entities.transaction import Transaction
from domain.entities.wallet_pair import WalletPair
from typing import List

from utils.general import get_response_from_entities


class ConversionDetail:
    def __init__(self, conversion_obj: Conversion, wallet_pair_obj: WalletPair, from_token_obj: Token,
                 to_token_obj: Token):
        self.conversion_obj = conversion_obj
        self.wallet_pair_obj = wallet_pair_obj
        self.from_token_obj = from_token_obj
        self.to_token_obj = to_token_obj

    def to_dict(self):
        conversion = {} if self.conversion_obj is None else self.conversion_obj.to_dict()
        wallet_pair = {} if self.wallet_pair_obj is None else self.wallet_pair_obj.to_dict()
        from_token = {} if self.from_token_obj is None else self.from_token_obj.to_dict()
        to_token = {} if self.to_token_obj is None else self.to_token_obj.to_dict()
        return {
            ConversionDetailEntities.CONVERSION.value: conversion,
            ConversionDetailEntities.WALLET_PAIR.value: wallet_pair,
            ConversionDetailEntities.FROM_TOKEN.value: from_token,
            ConversionDetailEntities.TO_TOKEN.value: to_token,
        }
