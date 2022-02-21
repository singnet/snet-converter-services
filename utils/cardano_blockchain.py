from blockfrost import BlockFrostApi, ApiUrls

from common.logger import get_logger

logger = get_logger(__name__)
JSON_RETURN_TYPE = "json"


class CardanoBlockchainUtil:

    def __init__(self, project_id: str, base_url: str = None, api_version: str = None):
        self.project_id = project_id
        self.base_url = base_url if base_url else ApiUrls.mainnet.value
        self.api_version = api_version
        self.blockchain_api = BlockFrostApi(project_id=project_id, base_url=base_url, api_version=api_version)

    def get_address_detail(self, address):
        return self.blockchain_api.address(address=address, return_type=JSON_RETURN_TYPE)

    def get_transaction_utxos(self, transaction_hash):
        return self.blockchain_api.transaction_utxos(hash=transaction_hash)

    def get_block(self, hash_or_number):
        logger.info(f"Getting the block detail for given hash or number={hash_or_number}")
        return self.blockchain_api.block(hash_or_number=hash_or_number, return_type=JSON_RETURN_TYPE)

    def get_transaction(self, hash):
        logger.info(f"Getting the transaction detail for given hash={hash}")
        return self.blockchain_api.transaction(hash=hash, return_type=JSON_RETURN_TYPE)