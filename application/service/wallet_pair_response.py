from constants.entity import WalletPairEntities


def get_wallet_pair_by_addresses_response(wallet_pair):
    return {
        WalletPairEntities.ROW_ID.value: wallet_pair[WalletPairEntities.ROW_ID.value],
        WalletPairEntities.ID.value: wallet_pair[WalletPairEntities.ROW_ID.value],
        WalletPairEntities.TOKEN_PAIR_ID.value: wallet_pair[WalletPairEntities.TOKEN_PAIR_ID.value],
        WalletPairEntities.FROM_ADDRESS.value: wallet_pair[WalletPairEntities.FROM_ADDRESS.value],
        WalletPairEntities.TO_ADDRESS.value: wallet_pair[WalletPairEntities.TO_ADDRESS.value],
        WalletPairEntities.DEPOSIT_ADDRESS.value: wallet_pair[WalletPairEntities.DEPOSIT_ADDRESS.value],
        WalletPairEntities.SIGNATURE.value: wallet_pair[WalletPairEntities.SIGNATURE.value],
        WalletPairEntities.SIGNATURE_EXPIRY.value: wallet_pair[WalletPairEntities.SIGNATURE_EXPIRY.value],
        WalletPairEntities.UPDATED_AT.value: wallet_pair[WalletPairEntities.UPDATED_AT.value]
    }


def create_wallet_pair_response(wallet_pair):
    return {
        WalletPairEntities.ROW_ID.value: wallet_pair[WalletPairEntities.ROW_ID.value],
        WalletPairEntities.ID.value: wallet_pair[WalletPairEntities.ID.value],
        WalletPairEntities.TOKEN_PAIR_ID.value: wallet_pair[WalletPairEntities.TOKEN_PAIR_ID.value],
        WalletPairEntities.FROM_ADDRESS.value: wallet_pair[WalletPairEntities.FROM_ADDRESS.value],
        WalletPairEntities.TO_ADDRESS.value: wallet_pair[WalletPairEntities.TO_ADDRESS.value],
        WalletPairEntities.DEPOSIT_ADDRESS.value: wallet_pair[WalletPairEntities.DEPOSIT_ADDRESS.value],
        WalletPairEntities.SIGNATURE.value: wallet_pair[WalletPairEntities.SIGNATURE.value],
        WalletPairEntities.SIGNATURE_EXPIRY.value: wallet_pair[WalletPairEntities.SIGNATURE_EXPIRY.value],
        WalletPairEntities.UPDATED_AT.value: wallet_pair[WalletPairEntities.UPDATED_AT.value]
    }


def get_wallet_pair_detail_by_deposit_address_response(wallet_pair):
    return {
        WalletPairEntities.ROW_ID.value: wallet_pair[WalletPairEntities.ROW_ID.value],
        WalletPairEntities.ID.value: wallet_pair[WalletPairEntities.ID.value]
    }


def get_wallet_pair_by_conversion_id_response(wallet_pair):
    return get_wallet_pair_by_addresses_response(wallet_pair)


def get_all_deposit_address_response(wallet_pairs):
    return [wallet_pair[WalletPairEntities.DEPOSIT_ADDRESS.value]  for wallet_pair in wallet_pairs]
