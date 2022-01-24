from constants.general import CreatedBy
from constants.status import ConversionStatus
from domain.factory.conversion_factory import ConversionFactory
from infrastructure.models import ConversionDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.general import get_uuid, datetime_in_utcnow


class ConversionRepository(BaseRepository):
    def create_conversion(self, wallet_pair_id, deposit_amount):
        conversion_item = ConversionDBModel(id=get_uuid(), wallet_pair_id=wallet_pair_id, deposit_amount=deposit_amount,
                                            claim_amount=None, fee_amount=None,
                                            status=ConversionStatus.USER_INITIATED.value, claim_signature=None,
                                            created_by=CreatedBy.DAPP.value, created_at=datetime_in_utcnow(),
                                            updated_at=datetime_in_utcnow())
        self.add_item(conversion_item)
        return ConversionFactory.conversion(row_id=conversion_item.row_id, id=conversion_item.id,
                                            wallet_pair_id=conversion_item.wallet_pair_id,
                                            deposit_amount=conversion_item.deposit_amount,
                                            claim_amount=conversion_item.claim_amount,
                                            fee_amount=conversion_item.fee_amount,
                                            status=conversion_item.status,
                                            claim_signature=conversion_item.claim_signature,
                                            created_by=conversion_item.created_by,
                                            created_at=conversion_item.created_at,
                                            updated_at=conversion_item.updated_at)

    def get_latest_user_pending_conversion_request(self, wallet_pair_id, status):
        conversion = self.session.query(ConversionDBModel.row_id, ConversionDBModel.id,
                                        ConversionDBModel.wallet_pair_id, ConversionDBModel.deposit_amount,
                                        ConversionDBModel.claim_amount, ConversionDBModel.fee_amount,
                                        ConversionDBModel.status, ConversionDBModel.claim_signature,
                                        ConversionDBModel.created_by, ConversionDBModel.created_at,
                                        ConversionDBModel.updated_at).filter(
            ConversionDBModel.wallet_pair_id == wallet_pair_id, ConversionDBModel.status == status).order_by(
            ConversionDBModel.created_at.asc()).first()

        if conversion is None:
            return None

        return ConversionFactory.conversion(row_id=conversion.row_id, id=conversion.id,
                                            wallet_pair_id=conversion.wallet_pair_id,
                                            deposit_amount=conversion.deposit_amount,
                                            claim_amount=conversion.claim_amount, fee_amount=conversion.fee_amount,
                                            status=conversion.status, claim_signature=conversion.claim_signature,
                                            created_by=conversion.created_by, created_at=conversion.created_at,
                                            updated_at=conversion.updated_at)

    def update_conversion_amount(self, conversion_id, deposit_amount):
        conversion = self.session.query(ConversionDBModel) \
            .filter(ConversionDBModel.id == conversion_id).one()
        conversion.deposit_amount = deposit_amount
        conversion.updated_at = datetime_in_utcnow()
        self.session.commit()

        if conversion is None:
            return None

        return ConversionFactory.conversion(row_id=conversion.row_id, id=conversion.id,
                                            wallet_pair_id=conversion.wallet_pair_id,
                                            deposit_amount=conversion.deposit_amount,
                                            claim_amount=conversion.claim_amount, fee_amount=conversion.fee_amount,
                                            status=conversion.status, claim_signature=conversion.claim_signature,
                                            created_by=conversion.created_by, created_at=conversion.created_at,
                                            updated_at=conversion.updated_at)
