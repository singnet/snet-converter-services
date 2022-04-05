from datetime import datetime

from domain.factory.PoolFactory import PoolFactory
from infrastructure.models import MessageGroupPoolDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.database import read_from_db, update_in_db


class PoolingRepository(BaseRepository):

    @read_from_db()
    def get_message_group_pool(self):
        message_pool = self.session.query(MessageGroupPoolDBModel.row_id, MessageGroupPoolDBModel.id,
                                          MessageGroupPoolDBModel.name, MessageGroupPoolDBModel.message_group_id,
                                          MessageGroupPoolDBModel.is_enabled, MessageGroupPoolDBModel.created_by,
                                          MessageGroupPoolDBModel.created_at, MessageGroupPoolDBModel.updated_at) \
            .filter(MessageGroupPoolDBModel.is_enabled.is_(True)) \
            .order_by(MessageGroupPoolDBModel.updated_at.asc()).first()

        if message_pool is None:
            return None

        return PoolFactory.message_pool(row_id=message_pool.row_id, id=message_pool.id, name=message_pool.name,
                                        message_group_id=message_pool.message_group_id,
                                        is_enabled=message_pool.is_enabled, created_by=message_pool.created_by,
                                        created_at=message_pool.created_at, updated_at=message_pool.updated_at)

    @update_in_db()
    def update_message_pool(self, id):
        message_pool = self.session.query(MessageGroupPoolDBModel) \
            .filter(MessageGroupPoolDBModel.id == id).one()
        if message_pool.trigger_count:
            message_pool.trigger_count += 1
        else:
            message_pool.trigger_count = 1
        message_pool.updated_at = datetime.now()
        self.session.commit()
