from datetime import date
from decimal import Decimal

from constants.entity import ConversionEntities
from utils.general import datetime_to_str


class Conversion:
    def __init__(self, row_id: int, id: str, wallet_pair_id: int, deposit_amount: Decimal, claim_amount: Decimal,
                 fee_amount: Decimal, status: str, claim_signature: str, created_by: str, created_at: date,
                 updated_at: date):
        self.row_id = int(row_id)
        self.id = id
        self.wallet_pair_id = int(wallet_pair_id)
        self.deposit_amount = str(deposit_amount.normalize())
        self.claim_amount = str(claim_amount.normalize())
        self.fee_amount = str(fee_amount.normalize())
        self.status = status
        self.claim_signature = claim_signature
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        return {
            ConversionEntities.ROW_ID.value: self.row_id,
            ConversionEntities.ID.value: self.id,
            ConversionEntities.WALLET_PAIR_ID.value: self.wallet_pair_id,
            ConversionEntities.DEPOSIT_AMOUNT.value: self.deposit_amount,
            ConversionEntities.CLAIM_AMOUNT.value: self.claim_amount,
            ConversionEntities.FEE_AMOUNT.value: self.fee_amount,
            ConversionEntities.STATUS.value: self.status,
            ConversionEntities.CLAIM_SIGNATURE.value: self.claim_signature,
            ConversionEntities.CREATED_BY.value: self.created_by,
            ConversionEntities.CREATED_AT.value: self.created_at,
            ConversionEntities.UPDATED_AT.value: self.updated_at
        }
