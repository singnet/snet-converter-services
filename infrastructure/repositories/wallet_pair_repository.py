from sqlalchemy import or_

from constants.general import CreatedBy
from domain.factory.wallet_pair_factory import WalletPairFactory
from infrastructure.models import WalletPairDBModel, ConversionDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.general import get_uuid, datetime_in_utcnow


class WalletPairRepository(BaseRepository):

    def get_wallet_pair_by_addresses(self, from_address, to_address, token_pair_id):
        wallet_pair = self.session.query(WalletPairDBModel.row_id, WalletPairDBModel.id,
                                         WalletPairDBModel.token_pair_id,
                                         WalletPairDBModel.from_address, WalletPairDBModel.to_address,
                                         WalletPairDBModel.deposit_address, WalletPairDBModel.signature,
                                         WalletPairDBModel.signature_metadata,
                                         WalletPairDBModel.signature_expiry, WalletPairDBModel.created_by,
                                         WalletPairDBModel.created_at, WalletPairDBModel.updated_at).filter(
            or_(WalletPairDBModel.from_address == from_address, WalletPairDBModel.from_address == to_address),
            or_(WalletPairDBModel.to_address == from_address, WalletPairDBModel.to_address == to_address),
            WalletPairDBModel.token_pair_id == token_pair_id,
            WalletPairDBModel.signature is not None).first()

        if wallet_pair is None:
            return None

        return WalletPairFactory.wallet_pair(row_id=wallet_pair.row_id, id=wallet_pair.id,
                                             token_pair_id=wallet_pair.token_pair_id,
                                             from_address=wallet_pair.from_address,
                                             to_address=wallet_pair.to_address,
                                             deposit_address=wallet_pair.deposit_address,
                                             signature=wallet_pair.signature,
                                             signature_metadata=wallet_pair.signature_metadata,
                                             signature_expiry=wallet_pair.signature_expiry,
                                             created_by=wallet_pair.created_by, created_at=wallet_pair.created_at,
                                             updated_at=wallet_pair.updated_at)

    def create_wallet_pair(self, from_address, to_address, token_pair_id, signature, signature_expiry,
                           signature_metadata, deposit_address):
        wallet_pair_item = WalletPairDBModel(id=get_uuid(), token_pair_id=token_pair_id, from_address=from_address,
                                             to_address=to_address, deposit_address=deposit_address,
                                             signature=signature, signature_metadata=signature_metadata,
                                             signature_expiry=signature_expiry, created_by=CreatedBy.DAPP.value,
                                             created_at=datetime_in_utcnow(), updated_at=datetime_in_utcnow())
        self.add_item(wallet_pair_item)

        return WalletPairFactory.wallet_pair(row_id=wallet_pair_item.row_id, id=wallet_pair_item.id,
                                             token_pair_id=wallet_pair_item.token_pair_id,
                                             from_address=wallet_pair_item.from_address,
                                             to_address=wallet_pair_item.to_address,
                                             deposit_address=wallet_pair_item.deposit_address,
                                             signature=wallet_pair_item.signature,
                                             signature_metadata=wallet_pair_item.signature_metadata,
                                             signature_expiry=wallet_pair_item.signature_expiry,
                                             created_by=wallet_pair_item.created_by,
                                             created_at=wallet_pair_item.created_at,
                                             updated_at=wallet_pair_item.updated_at)

    def get_wallet_pair_by_deposit_address(self, deposit_address):
        wallet_pair = self.session.query(WalletPairDBModel).filter(WalletPairDBModel.deposit_address == deposit_address) \
            .order_by(WalletPairDBModel.created_at.desc()).first()

        if wallet_pair is None:
            return None

        return WalletPairFactory.wallet_pair(row_id=wallet_pair.row_id, id=wallet_pair.id,
                                             token_pair_id=wallet_pair.token_pair_id,
                                             from_address=wallet_pair.from_address,
                                             to_address=wallet_pair.to_address,
                                             deposit_address=wallet_pair.deposit_address,
                                             signature=wallet_pair.signature,
                                             signature_metadata=wallet_pair.signature_metadata,
                                             signature_expiry=wallet_pair.signature_expiry,
                                             created_by=wallet_pair.created_by, created_at=wallet_pair.created_at,
                                             updated_at=wallet_pair.updated_at)

    def get_wallet_pair_by_conversion_id(self, conversion_id):
        wallet_pair = self.session.query(WalletPairDBModel) \
            .join(ConversionDBModel, ConversionDBModel.wallet_pair_id == WalletPairDBModel.row_id) \
            .filter(ConversionDBModel.id == conversion_id).first()

        if wallet_pair is None:
            return None

        return WalletPairFactory.wallet_pair(row_id=wallet_pair.row_id, id=wallet_pair.id,
                                             token_pair_id=wallet_pair.token_pair_id,
                                             from_address=wallet_pair.from_address,
                                             to_address=wallet_pair.to_address,
                                             deposit_address=wallet_pair.deposit_address,
                                             signature=wallet_pair.signature,
                                             signature_metadata=wallet_pair.signature_metadata,
                                             signature_expiry=wallet_pair.signature_expiry,
                                             created_by=wallet_pair.created_by, created_at=wallet_pair.created_at,
                                             updated_at=wallet_pair.updated_at)

    def get_all_deposit_address(self):
        wallet_pairs = self.session.query(WalletPairDBModel) \
            .filter(WalletPairDBModel.deposit_address.isnot(None)).all()

        return [WalletPairFactory.wallet_pair(row_id=wallet_pair.row_id, id=wallet_pair.id,
                                              token_pair_id=wallet_pair.token_pair_id,
                                              from_address=wallet_pair.from_address,
                                              to_address=wallet_pair.to_address,
                                              deposit_address=wallet_pair.deposit_address,
                                              signature=wallet_pair.signature,
                                              signature_metadata=wallet_pair.signature_metadata,
                                              signature_expiry=wallet_pair.signature_expiry,
                                              created_by=wallet_pair.created_by, created_at=wallet_pair.created_at,
                                              updated_at=wallet_pair.updated_at) for wallet_pair in wallet_pairs]
