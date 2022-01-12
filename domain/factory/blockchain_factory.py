from domain.entities.blockchain import Blockchain


class BlockchainFactory:
    def __init__(self):
        pass

    @staticmethod
    def blockchain(id, name=None, description=None, symbol=None, logo=None, chain_id=None,
                   block_confirmation=None, is_extension_available=None, created_by=None, created_at=None,
                   updated_at=None):
        return Blockchain(id=id, name=name, description=description, symbol=symbol, logo=logo, chain_id=chain_id,
                          block_confirmation=block_confirmation, is_extension_available=is_extension_available,
                          created_by=created_by, created_at=created_at, updated_at=updated_at)
