from common.logger import get_logger
from infrastructure.repositories.pooling_repository import PoolingRepository

logger = get_logger(__name__)


class PoolingService:

    def __init__(self):
        self.pooling_repo = PoolingRepository()

    def get_message_group_pool(self):
        logger.info("Getting the message group pool which is last least used for processing")
        message_pool = self.pooling_repo.get_message_group_pool()
        return message_pool.to_dict() if message_pool else None

    def update_message_pool(self, id):
        logger.info(f"Updating the message pool id={id}")
        self.pooling_repo.update_message_pool(id=id)
