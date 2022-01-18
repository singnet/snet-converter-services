from datetime import date

from constants.entity import BlockchainEntities
from utils.general import datetime_to_str


class Blockchain:
    def __init__(self, id: str, name: str, description: str, symbol: str, logo: str, chain_id: str,
                 block_confirmation: int, is_extension_available: bool, created_by: str, created_at: date,
                 updated_at: date):
        self.id = id
        self.name = name
        self.description = description
        self.symbol = symbol
        self.logo = logo
        self.chain_id = chain_id.split(",")
        self.block_confirmation = block_confirmation
        self.is_extension_available = is_extension_available
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        return {
            BlockchainEntities.ID.value: self.id,
            BlockchainEntities.NAME.value: self.name,
            BlockchainEntities.DESCRIPTION.value: self.description,
            BlockchainEntities.SYMBOL.value: self.symbol,
            BlockchainEntities.LOGO.value: self.logo,
            BlockchainEntities.CHAIN_ID.value: self.chain_id,
            BlockchainEntities.BLOCK_CONFIRMATION.value: self.block_confirmation,
            BlockchainEntities.IS_EXTENSION_AVAILABLE.value: bool(self.is_extension_available),
            BlockchainEntities.CREATED_BY.value: self.created_by,
            BlockchainEntities.CREATED_AT.value: self.created_at,
            BlockchainEntities.UPDATED_AT.value: self.updated_at
        }
