from application.service.wallet_pair_response import get_wallet_pair_by_addresses_response, create_wallet_pair_response
from common.logger import get_logger
from constants.entity import TokenPairEntities, BlockchainEntities, TokenEntities
from infrastructure.repositories.wallet_pair_repository import WalletPairRepository
from utils.blockchain import get_deposit_address
from utils.signature import create_signature_metadata

logger = get_logger(__name__)


class WalletPairService:

    def __init__(self):
        self.wallet_pair_repo = WalletPairRepository()

    def create_wallet_pair(self, from_address, to_address, token_pair_id, signature, signature_expiry,
                           signature_metadata, deposit_address):
        wallet_pair = self.wallet_pair_repo.create_wallet_pair(from_address, to_address, token_pair_id, signature,
                                                               signature_expiry, signature_metadata, deposit_address)
        return create_wallet_pair_response(wallet_pair.to_dict()) if wallet_pair else None

    def get_wallet_pair_by_addresses(self, from_address, to_address, token_pair_id):
        wallet_pair = self.wallet_pair_repo.get_wallet_pair_by_addresses(from_address=from_address,
                                                                         to_address=to_address,
                                                                         token_pair_id=token_pair_id)
        return get_wallet_pair_by_addresses_response(wallet_pair.to_dict()) if wallet_pair else None

    def persist_wallet_pair_details(self, from_address, to_address, amount, signature, block_number, token_pair):
        token_pair_row_id = token_pair.get(TokenPairEntities.ROW_ID.value, None)
        token_pair_id = token_pair.get(TokenPairEntities.ID.value, None)

        wallet_pair = self.get_wallet_pair_by_addresses(from_address=from_address, to_address=to_address,
                                                        token_pair_id=token_pair_row_id)

        # persist only when it's not present
        if wallet_pair is None:
            from_blockchain_name = token_pair.get(TokenPairEntities.FROM_TOKEN.value, {}).get(
                TokenEntities.BLOCKCHAIN.value, {}).get(
                BlockchainEntities.NAME.value, None)
            signature_metadata = create_signature_metadata(token_pair_id=token_pair_id, amount=amount,
                                                           from_address=from_address, to_address=to_address,
                                                           block_number=block_number)
            wallet_pair = self.create_wallet_pair(from_address=from_address, to_address=to_address,
                                                  token_pair_id=token_pair_row_id,
                                                  signature=signature, signature_expiry=None,
                                                  signature_metadata=signature_metadata,
                                                  deposit_address=get_deposit_address(
                                                      blockchain_name=from_blockchain_name))
        return wallet_pair
