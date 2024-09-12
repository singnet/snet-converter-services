from domain.factory.blockchain_factory import BlockchainFactory
from infrastructure.models import BlockChainDBModel, TokenDBModel, TokenPairDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.database import read_from_db


class BlockchainRepository(BaseRepository):

    @read_from_db()
    def get_all_blockchain(self):
        blockchains = self.session.query(BlockChainDBModel.id, BlockChainDBModel.name, BlockChainDBModel.description,
                                         BlockChainDBModel.symbol, BlockChainDBModel.logo, BlockChainDBModel.chain_id,
                                         BlockChainDBModel.block_confirmation, BlockChainDBModel.is_extension_available,
                                         BlockChainDBModel.created_by, BlockChainDBModel.created_at,
                                         BlockChainDBModel.updated_at) \
            .order_by(BlockChainDBModel.is_extension_available.desc(), BlockChainDBModel.name.asc()).all()

        return [BlockchainFactory.blockchain(id=blockchain.id, name=blockchain.name, description=blockchain.description,
                                             symbol=blockchain.symbol, logo=blockchain.logo,
                                             chain_id=blockchain.chain_id,
                                             block_confirmation=blockchain.block_confirmation,
                                             is_extension_available=blockchain.is_extension_available,
                                             created_by=blockchain.created_by, created_at=blockchain.created_at,
                                             updated_at=blockchain.updated_at)
                for blockchain in blockchains]

    @read_from_db()
    def get_blockchain(self, name):
        blockchain = self.session.query(BlockChainDBModel) \
            .filter(BlockChainDBModel.name.ilike(name)).first()

        if blockchain is None:
            return None

        return BlockchainFactory.blockchain(id=blockchain.id, name=blockchain.name, description=blockchain.description,
                                            symbol=blockchain.symbol, logo=blockchain.logo,
                                            chain_id=blockchain.chain_id,
                                            block_confirmation=blockchain.block_confirmation,
                                            is_extension_available=blockchain.is_extension_available,
                                            created_by=blockchain.created_by, created_at=blockchain.created_at,
                                            updated_at=blockchain.updated_at)

    @read_from_db()
    def get_to_token_data_by_token_pair_id(self, token_pair_id):
        chain_data = self.session.query(
            BlockChainDBModel.name,
            BlockChainDBModel.chain_id,
            TokenDBModel.symbol,
            TokenDBModel.contract_address
        ).join(
            TokenPairDBModel, TokenPairDBModel.to_token_id == TokenDBModel.row_id
        ).join(
            BlockChainDBModel, TokenDBModel.blockchain_id == BlockChainDBModel.row_id
        ).filter(
            TokenPairDBModel.id == token_pair_id
        )

        return chain_data.one_or_none()
