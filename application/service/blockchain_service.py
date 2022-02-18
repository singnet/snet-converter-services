from application.service.blockchain_response import get_all_blockchain_response, get_blockchain_response
from common.logger import get_logger
from infrastructure.repositories.blockchain_repository import BlockchainRepository
from utils.general import get_response_from_entities

logger = get_logger(__name__)


class BlockchainService:

    def __init__(self):
        self.blockchain_repo = BlockchainRepository()

    def get_all_blockchain(self):
        logger.info("Getting all the available blockchain")
        blockchains = self.blockchain_repo.get_all_blockchain()
        return get_all_blockchain_response(get_response_from_entities(blockchains))

    def get_blockchain(self, blockchain_name):
        logger.info(f"Getting the blockchain detail for blockchain_name={blockchain_name}")
        blockchain = self.blockchain_repo.get_blockchain(name=blockchain_name)
        return get_blockchain_response(blockchain.to_dict()) if blockchain else None

