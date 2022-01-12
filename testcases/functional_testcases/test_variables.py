from datetime import datetime

from infrastructure.models import BlockChainDBModel

DAPP_AS_CREATED_BY = "DApp"


def create_blockchain_record(id, name, description, symbol, logo, chain_id, block_confirmation, is_extension_available,
                             created_by, created_at, updated_at):
    return BlockChainDBModel(id=id, name=name, description=description, symbol=symbol,
                             logo=logo, chain_id=chain_id, block_confirmation=block_confirmation,
                             is_extension_available=is_extension_available, created_by=created_by,
                             created_at=created_at, updated_at=updated_at)


class TestVariablesBlockchain:
    def __init__(self):
        created_at = "2022-01-12 04:10:54"
        updated_at = "2022-01-12 04:10:54"
        self.blockchain_id_1 = "a38b4038c3a04810805fb26056dfabdd"
        self.blockchain_id_2 = "5b21294fe71a4145a40f6ab918a50f96"
        self.blockchain = [
            create_blockchain_record(id=self.blockchain_id_1, name="Ethereum", description="Connect with your wallet",
                                     symbol="ETH", logo="www.ethereum.com/image.png", chain_id="42,3", block_confirmation=25,
                                     is_extension_available=True, created_by=DAPP_AS_CREATED_BY, created_at=created_at,
                                     updated_at=updated_at),
            create_blockchain_record(id=self.blockchain_id_2, name="Cardano", description="Add your wallet address",
                                     symbol="ADA", logo="www.cardano.com/image.png", chain_id="2", block_confirmation=23,
                                     is_extension_available=False, created_by=DAPP_AS_CREATED_BY, created_at=created_at,
                                     updated_at=updated_at)
        ]
