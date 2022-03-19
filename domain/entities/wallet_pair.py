from datetime import date

from constants.entity import WalletPairEntities
from utils.general import datetime_to_str


class WalletPair:

    def __init__(self, row_id: int, id: str, token_pair_id: int, from_address: str, to_address: str,
                 deposit_address: str, deposit_address_detail: dict, signature: str, signature_metadata: dict,
                 signature_expiry: date,
                 created_by: str, created_at: date,
                 updated_at: date):
        self.row_id = row_id
        self.id = id
        self.token_pair_id = token_pair_id
        self.from_address = from_address
        self.to_address = to_address
        self.deposit_address = deposit_address
        self.deposit_address_detail = deposit_address_detail
        self.signature = signature
        self.signature_metadata = signature_metadata
        self.signature_expiry = datetime_to_str(signature_expiry) if signature_expiry else None
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        return {
            WalletPairEntities.ROW_ID.value: self.row_id,
            WalletPairEntities.ID.value: self.id,
            WalletPairEntities.TOKEN_PAIR_ID.value: self.token_pair_id,
            WalletPairEntities.FROM_ADDRESS.value: self.from_address,
            WalletPairEntities.TO_ADDRESS.value: self.to_address,
            WalletPairEntities.DEPOSIT_ADDRESS.value: self.deposit_address,
            WalletPairEntities.DEPOSIT_ADDRESS_DETAIL.value: self.deposit_address_detail,
            WalletPairEntities.SIGNATURE.value: self.signature,
            WalletPairEntities.SIGNATURE_METADATA.value: self.signature_metadata,
            WalletPairEntities.SIGNATURE_EXPIRY.value: self.signature_expiry,
            WalletPairEntities.CREATED_BY.value: self.created_by,
            WalletPairEntities.CREATED_AT.value: self.created_at,
            WalletPairEntities.UPDATED_AT.value: self.updated_at,
        }
