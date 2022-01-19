from domain.entities.wallet_pair import WalletPair


class WalletPairFactory:

    @staticmethod
    def wallet_pair(row_id, id, token_pair_id, from_address, to_address, signature, signature_metadata, created_by,
                    created_at, updated_at, signature_expiry=None, deposit_address=None):
        return WalletPair(row_id=row_id, id=id, token_pair_id=token_pair_id, from_address=from_address,
                          to_address=to_address, deposit_address=deposit_address, signature=signature,
                          signature_metadata=signature_metadata,
                          signature_expiry=signature_expiry, created_by=created_by, created_at=created_at,
                          updated_at=updated_at)
