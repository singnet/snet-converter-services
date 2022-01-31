from blockfrost import BlockFrostApi, ApiUrls


class CardanoBlockchainUtil:

    def __init__(self, project_id: str, base_url: str = None, api_version: str = None):
        self.project_id = project_id
        self.base_url = base_url if base_url else ApiUrls.mainnet.value
        self.api_version = api_version
        self.blockchain_api = BlockFrostApi(project_id=project_id, base_url=base_url, api_version=api_version)

    def get_address_detail(self, address):
        return self.blockchain_api.address(address=address)

    def get_transaction_utxos(self, transaction_hash):
        return self.blockchain_api.transaction_utxos(hash=transaction_hash)

