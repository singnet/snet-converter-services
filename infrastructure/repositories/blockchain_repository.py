from domain.factory.blockchain_factory import BlockchainFactory
from infrastructure.models import BlockChainDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.general import datetime_to_str


class BlockchainRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get_all_blockchain(self):
        blockchains = self.session.query(BlockChainDBModel.id, BlockChainDBModel.name, BlockChainDBModel.description,
                                         BlockChainDBModel.symbol, BlockChainDBModel.logo, BlockChainDBModel.chain_id,
                                         BlockChainDBModel.block_confirmation, BlockChainDBModel.is_extension_available,
                                         BlockChainDBModel.created_by, BlockChainDBModel.created_at,
                                         BlockChainDBModel.updated_at).order_by(BlockChainDBModel.name.asc()).all()

        return [BlockchainFactory.blockchain(id=blockchain.id, name=blockchain.name, description=blockchain.description,
                                             symbol=blockchain.symbol, logo=blockchain.logo,
                                             chain_id=blockchain.chain_id,
                                             block_confirmation=blockchain.block_confirmation,
                                             is_extension_available=blockchain.is_extension_available,
                                             created_by=blockchain.created_by,
                                             created_at=blockchain.created_at,
                                             updated_at=blockchain.updated_at)
                for blockchain in blockchains]
