from datetime import date

from constants.entity import MessagePoolEntities
from utils.general import datetime_to_str


class MessagePool:

    def __init__(self, row_id: int, id: str, name: str, message_group_id: str, is_enabled: bool, created_by: str,
                 created_at: date, updated_at: date):
        self.row_id = row_id
        self.id = id
        self.name = name
        self.message_group_id = message_group_id
        self.is_enabled = is_enabled
        self.created_by = created_by
        self.created_at = datetime_to_str(created_at)
        self.updated_at = datetime_to_str(updated_at)

    def to_dict(self):
        return {
            MessagePoolEntities.ROW_ID.value: self.row_id,
            MessagePoolEntities.ID.value: self.id,
            MessagePoolEntities.NAME.value: self.name,
            MessagePoolEntities.MESSAGE_GROUP_ID.value: self.message_group_id,
            MessagePoolEntities.IS_ENABLED.value: self.is_enabled,
            MessagePoolEntities.CREATED_BY.value: self.created_by,
            MessagePoolEntities.CREATED_AT.value: self.created_at,
            MessagePoolEntities.UPDATED_AT.value: self.updated_at,
        }
