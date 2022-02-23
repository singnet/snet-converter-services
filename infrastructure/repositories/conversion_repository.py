from sqlalchemy import or_
from sqlalchemy.orm import aliased

from constants.general import CreatedBy
from constants.status import ConversionStatus, ConversionTransactionStatus
from domain.factory.conversion_factory import ConversionFactory
from infrastructure.models import ConversionDBModel, WalletPairDBModel, TokenPairDBModel, TokenDBModel, \
    BlockChainDBModel, ConversionTransactionDBModel, TransactionDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.general import get_uuid, datetime_in_utcnow


class ConversionRepository(BaseRepository):

    def get_conversion_detail(self, conversion_id):
        from_token = aliased(TokenDBModel)
        to_token = aliased(TokenDBModel)
        from_blockchain = aliased(BlockChainDBModel)
        to_blockchain = aliased(BlockChainDBModel)

        conversion = self.session.query(ConversionDBModel, WalletPairDBModel, from_token, to_token, from_blockchain,
                                        to_blockchain) \
            .join(WalletPairDBModel, WalletPairDBModel.row_id == ConversionDBModel.wallet_pair_id) \
            .join(TokenPairDBModel, TokenPairDBModel.row_id == WalletPairDBModel.token_pair_id) \
            .join(from_token, from_token.row_id == TokenPairDBModel.from_token_id) \
            .join(to_token, to_token.row_id == TokenPairDBModel.to_token_id) \
            .join(from_blockchain, from_blockchain.row_id == from_token.blockchain_id) \
            .join(to_blockchain, to_blockchain.row_id == to_token.blockchain_id).filter(
            ConversionDBModel.id == conversion_id).first()

        if conversion is None:
            return None

        transaction_detail = self.get_transaction_detail(conversion_ids=[conversion_id])

        return ConversionFactory.conversion_detail(conversion=conversion[0], wallet_pair=conversion[1],
                                                   from_token=conversion[2], to_token=conversion[3],
                                                   from_blockchain=conversion[4], to_blockchain=conversion[5],
                                                   transactions=transaction_detail.get(conversion[0].id, {}))

    def get_transaction_detail(self, conversion_ids):
        transaction_details = self.session.query(ConversionDBModel.id, TransactionDBModel) \
            .join(ConversionTransactionDBModel, ConversionTransactionDBModel.conversion_id == ConversionDBModel.row_id) \
            .join(TransactionDBModel,
                  TransactionDBModel.conversion_transaction_id == ConversionTransactionDBModel.row_id) \
            .filter(ConversionTransactionDBModel.status != ConversionTransactionStatus.FAILED.value,
                    ConversionDBModel.id.in_(conversion_ids)) \
            .order_by(ConversionTransactionDBModel.row_id, ConversionTransactionDBModel.updated_at.asc()).all()

        return ConversionFactory.convert_transaction_by_conversion_id(transaction_details=transaction_details)

    def create_conversion(self, wallet_pair_id, deposit_amount, created_by):
        conversion_item = ConversionDBModel(id=get_uuid(), wallet_pair_id=wallet_pair_id, deposit_amount=deposit_amount,
                                            claim_amount=None, fee_amount=None,
                                            status=ConversionStatus.USER_INITIATED.value, claim_signature=None,
                                            created_by=created_by, created_at=datetime_in_utcnow(),
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

    def create_conversion_transaction(self, conversion_id, created_by):
        conversion_transaction_item = ConversionTransactionDBModel(id=get_uuid(), conversion_id=conversion_id,
                                                                   status=ConversionTransactionStatus.PROCESSING.value,
                                                                   created_by=created_by,
                                                                   created_at=datetime_in_utcnow(),
                                                                   updated_at=datetime_in_utcnow())
        self.add_item(conversion_transaction_item)
        return ConversionFactory.conversion_transaction(row_id=conversion_transaction_item.row_id,
                                                        id=conversion_transaction_item.id,
                                                        conversion_id=conversion_transaction_item.conversion_id,
                                                        status=conversion_transaction_item.status,
                                                        created_by=conversion_transaction_item.created_by,
                                                        created_at=conversion_transaction_item.created_at,
                                                        updated_at=conversion_transaction_item.updated_at)

    def create_transaction(self, conversion_transaction_id, from_token_id, to_token_id, transaction_visibility,
                           transaction_operation, transaction_hash, transaction_amount, status, created_by):
        if not created_by:
            created_by = CreatedBy.DAPP.value

        transaction_item = TransactionDBModel(id=get_uuid(), conversion_transaction_id=conversion_transaction_id,
                                              from_token_id=from_token_id, to_token_id=to_token_id,
                                              transaction_visibility=transaction_visibility,
                                              transaction_operation=transaction_operation,
                                              transaction_hash=transaction_hash, transaction_amount=transaction_amount,
                                              status=status,
                                              created_by=created_by,
                                              created_at=datetime_in_utcnow(),
                                              updated_at=datetime_in_utcnow())
        self.add_item(transaction_item)
        return ConversionFactory.transaction(row_id=transaction_item.row_id,
                                             id=transaction_item.id,
                                             conversion_transaction_id=transaction_item.conversion_transaction_id,
                                             from_token_id=transaction_item.from_token_id,
                                             to_token_id=transaction_item.to_token_id,
                                             transaction_visibility=transaction_item.transaction_visibility,
                                             transaction_operation=transaction_item.transaction_operation,
                                             transaction_hash=transaction_item.transaction_hash,
                                             transaction_amount=transaction_item.transaction_amount,
                                             status=transaction_item.status,
                                             created_by=transaction_item.created_by,
                                             created_at=transaction_item.created_at,
                                             updated_at=transaction_item.updated_at)

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

    def update_conversion_status(self, conversion_id, status):
        conversion = self.session.query(ConversionDBModel) \
            .filter(ConversionDBModel.id == conversion_id).one()
        conversion.status = status
        conversion.updated_at = datetime_in_utcnow()
        self.session.commit()

    def update_conversion(self, conversion_id, deposit_amount, claim_amount, fee_amount, status):
        conversion = self.session.query(ConversionDBModel) \
            .filter(ConversionDBModel.id == conversion_id).first()
        if deposit_amount:
            conversion.deposit_amount = deposit_amount
        if claim_amount:
            conversion.claim_amount = claim_amount
        if fee_amount:
            conversion.fee_amount = fee_amount
        if status:
            conversion.status = status

        conversion.updated_at = datetime_in_utcnow()
        self.session.commit()

    def update_conversion_transaction(self, conversion_transaction_id, status):
        conversion_transaction = self.session.query(ConversionTransactionDBModel) \
            .filter(ConversionTransactionDBModel.row_id == conversion_transaction_id).first()

        conversion_transaction.status = status
        conversion_transaction.updated_at = datetime_in_utcnow()
        self.session.commit()

    def get_token_contract_address_for_conversion_id(self, conversion_id):
        contract_address = self.session.query(TokenPairDBModel.contract_address) \
            .join(WalletPairDBModel, WalletPairDBModel.token_pair_id == TokenPairDBModel.row_id) \
            .join(ConversionDBModel, ConversionDBModel.wallet_pair_id == WalletPairDBModel.row_id) \
            .filter(ConversionDBModel.id == conversion_id).first()

        if not contract_address:
            return None

        return contract_address[0]

    def get_conversion_history(self, address, conversion_id):
        from_token = aliased(TokenDBModel)
        to_token = aliased(TokenDBModel)
        from_blockchain = aliased(BlockChainDBModel)
        to_blockchain = aliased(BlockChainDBModel)

        conversions_detail_query = self.session.query(ConversionDBModel, WalletPairDBModel, from_token, to_token,
                                                      from_blockchain, to_blockchain) \
            .join(WalletPairDBModel, WalletPairDBModel.row_id == ConversionDBModel.wallet_pair_id) \
            .join(TokenPairDBModel, TokenPairDBModel.row_id == WalletPairDBModel.token_pair_id) \
            .join(from_token, from_token.row_id == TokenPairDBModel.from_token_id) \
            .join(to_token, to_token.row_id == TokenPairDBModel.to_token_id) \
            .join(from_blockchain, from_blockchain.row_id == from_token.blockchain_id) \
            .join(to_blockchain, to_blockchain.row_id == to_token.blockchain_id) \
            .order_by(ConversionDBModel.created_at.desc())

        if address:
            conversions_detail_query = conversions_detail_query.filter(
                or_(WalletPairDBModel.from_address == address, WalletPairDBModel.to_address == address))
        if conversion_id:
            conversions_detail_query = conversions_detail_query.filter(ConversionDBModel.id == conversion_id)

        conversions_detail = conversions_detail_query.all()

        conversion_ids = ConversionFactory.get_conversion_ids(conversions_detail=conversions_detail)

        transaction_detail = self.get_transaction_detail(conversion_ids=conversion_ids)

        return [ConversionFactory.conversion_detail(conversion=conversion_detail[0], wallet_pair=conversion_detail[1],
                                                    from_token=conversion_detail[2], to_token=conversion_detail[3],
                                                    from_blockchain=conversion_detail[4],
                                                    to_blockchain=conversion_detail[5],
                                                    transactions=transaction_detail.get(conversion_detail[0].id, {}))
                for conversion_detail in conversions_detail]

    def get_waiting_conversion_deposit_on_address(self, deposit_address):
        conversion = self.session.query(ConversionDBModel) \
            .join(WalletPairDBModel, WalletPairDBModel.row_id == ConversionDBModel.wallet_pair_id) \
            .filter(WalletPairDBModel.deposit_address == deposit_address,
                    ConversionDBModel.status == ConversionStatus.USER_INITIATED.value) \
            .order_by(ConversionDBModel.created_by.desc()).first()

        if conversion is None:
            return None

        return ConversionFactory.conversion(row_id=conversion.row_id, id=conversion.id,
                                            wallet_pair_id=conversion.wallet_pair_id,
                                            deposit_amount=conversion.deposit_amount,
                                            claim_amount=conversion.claim_amount, fee_amount=conversion.fee_amount,
                                            status=conversion.status, claim_signature=conversion.claim_signature,
                                            created_by=conversion.created_by, created_at=conversion.created_at,
                                            updated_at=conversion.updated_at)

    def update_transaction_by_id(self, tx_id, tx_operation, tx_visibility, tx_amount, tx_status, created_by):
        transaction = self.session.query(TransactionDBModel) \
            .filter(TransactionDBModel.id == tx_id).one()
        if tx_operation:
            transaction.transaction_operation = tx_operation
        if tx_visibility:
            transaction.transaction_visibility = tx_visibility
        if tx_amount:
            transaction.transaction_amount = tx_amount
        if tx_status:
            transaction.status = tx_status
        if created_by:
            transaction.created_by = created_by
        transaction.updated_at = datetime_in_utcnow()
        self.session.commit()

    def get_transaction_by_hash(self, tx_hash):
        transaction = self.session.query(TransactionDBModel) \
            .filter(TransactionDBModel.transaction_hash == tx_hash).first()

        if transaction is None:
            return None

        return ConversionFactory.transaction(row_id=transaction.row_id,
                                             id=transaction.id,
                                             conversion_transaction_id=transaction.conversion_transaction_id,
                                             from_token_id=transaction.from_token_id,
                                             to_token_id=transaction.to_token_id,
                                             transaction_visibility=transaction.transaction_visibility,
                                             transaction_operation=transaction.transaction_operation,
                                             transaction_hash=transaction.transaction_hash,
                                             transaction_amount=transaction.transaction_amount,
                                             status=transaction.status,
                                             created_by=transaction.created_by,
                                             created_at=transaction.created_at,
                                             updated_at=transaction.updated_at)

    def get_conversion_detail_by_tx_id(self, tx_id):
        conversion = self.session.query(ConversionDBModel) \
            .join(ConversionTransactionDBModel, ConversionTransactionDBModel.conversion_id == ConversionDBModel.row_id) \
            .join(TransactionDBModel,
                  TransactionDBModel.conversion_transaction_id == ConversionTransactionDBModel.row_id) \
            .filter(TransactionDBModel.id == tx_id).first()

        return ConversionFactory.conversion(row_id=conversion.row_id, id=conversion.id,
                                            wallet_pair_id=conversion.wallet_pair_id,
                                            deposit_amount=conversion.deposit_amount,
                                            claim_amount=conversion.claim_amount, fee_amount=conversion.fee_amount,
                                            status=conversion.status, claim_signature=conversion.claim_signature,
                                            created_by=conversion.created_by, created_at=conversion.created_at,
                                            updated_at=conversion.updated_at)
