from datetime import date

from constants.entity import TradingViewEntities
from utils.general import datetime_to_str


class TradingView:

    def __init__(self, row_id: int, id_: str, symbol: str, alt_text: str, created_at: date, updated_at: date):
        self.row_id = row_id
        self.id = id_
        self.symbol = symbol
        self.alt_text = alt_text
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        return {
            TradingViewEntities.ROW_ID.value: self.row_id,
            TradingViewEntities.ID.value: self.id,
            TradingViewEntities.SYMBOL.value: self.symbol,
            TradingViewEntities.ALT_TEXT.value: self.alt_text,
            TradingViewEntities.CREATED_AT.value: self.created_at,
            TradingViewEntities.UPDATED_AT.value: self.updated_at
        }
