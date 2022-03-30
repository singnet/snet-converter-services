from sqlalchemy import or_, case, func, and_
from sqlalchemy.orm import joinedload, aliased

from constants.general import CreatedBy, BlockchainName
from constants.status import ConversionStatus, ConversionTransactionStatus
from domain.factory.conversion_factory import ConversionFactory
from infrastructure.models import ConversionDBModel, WalletPairDBModel, TokenPairDBModel, TokenDBModel, \
    ConversionTransactionDBModel, TransactionDBModel, BlockChainDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.database import read_from_db, update_in_db
from utils.general import get_uuid, datetime_in_utcnow


class ConversionRepository(BaseRepository):

    @read_from_db()
    def get_conversion_count_by_status(self, address):
        status_counts = self.session.query(ConversionDBModel.status, func.count(ConversionDBModel.id).label("count")) \
            .join(WalletPairDBModel, WalletPairDBModel.row_id == ConversionDBModel.wallet_pair_id) \
            .filter(
            or_(WalletPairDBModel.from_address == address, WalletPairDBModel.to_address == address)) \
            .group_by(ConversionDBModel.status) \
            .all()

        return ConversionFactory.conversion_status_count(status_counts)

    @read_from_db()
    def get_conversion_detail(self, conversion_id):
        conversion_detail_query = self.session.query(ConversionDBModel) \
            .join(WalletPairDBModel, WalletPairDBModel.row_id == ConversionDBModel.wallet_pair_id) \
            .join(TokenPairDBModel, TokenPairDBModel.row_id == WalletPairDBModel.token_pair_id) \
            .filter(ConversionDBModel.id == conversion_id)

        conversion_detail = conversion_detail_query.options(joinedload(ConversionDBModel.wallet_pair)).options(
            joinedload(ConversionDBModel.wallet_pair).joinedload(WalletPairDBModel.token_pair)).first()

        if conversion_detail is None:
            return None

        return ConversionFactory.conversion_detail(conversion=conversion_detail)

    def create_conversion(self, wallet_pair_id, deposit_amount, fee_amount, claim_amount, created_by):
        conversion_item = ConversionDBModel(id=get_uuid(), wallet_pair_id=wallet_pair_id, deposit_amount=deposit_amount,
                                            claim_amount=claim_amount, fee_amount=fee_amount,
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

    def create_transaction(self, conversion_transaction_id, token_id, transaction_visibility,
                           transaction_operation, transaction_hash, transaction_amount, confirmation, status,
                           created_by):
        if not created_by:
            created_by = CreatedBy.DAPP.value

        transaction_item = TransactionDBModel(id=get_uuid(), conversion_transaction_id=conversion_transaction_id,
                                              token_id=token_id, transaction_visibility=transaction_visibility,
                                              transaction_operation=transaction_operation,
                                              transaction_hash=transaction_hash, transaction_amount=transaction_amount,
                                              confirmation=confirmation, status=status, created_by=created_by,
                                              created_at=datetime_in_utcnow(), updated_at=datetime_in_utcnow())
        self.add_item(transaction_item)
        return ConversionFactory.transaction(row_id=transaction_item.row_id,
                                             id=transaction_item.id,
                                             conversion_transaction_id=transaction_item.conversion_transaction_id,
                                             token_id=transaction_item.token_id,
                                             transaction_visibility=transaction_item.transaction_visibility,
                                             transaction_operation=transaction_item.transaction_operation,
                                             transaction_hash=transaction_item.transaction_hash,
                                             transaction_amount=transaction_item.transaction_amount,
                                             confirmation=transaction_item.confirmation,
                                             status=transaction_item.status,
                                             created_by=transaction_item.created_by,
                                             created_at=transaction_item.created_at,
                                             updated_at=transaction_item.updated_at, conversion_transaction_obj=None,
                                             token_obj=None)

    @read_from_db()
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

    @update_in_db()
    def update_conversion_status(self, conversion_id, status):
        conversion = self.session.query(ConversionDBModel) \
            .filter(ConversionDBModel.id == conversion_id).one()
        conversion.status = status
        conversion.updated_at = datetime_in_utcnow()
        self.session.commit()

    @update_in_db()
    def update_conversion(self, conversion_id, deposit_amount, claim_amount, fee_amount, status, claim_signature):
        conversion = self.session.query(ConversionDBModel) \
            .filter(ConversionDBModel.id == conversion_id).first()
        if deposit_amount:
            conversion.deposit_amount = deposit_amount
        if claim_amount:
            conversion.claim_amount = claim_amount
        if fee_amount is not None:
            conversion.fee_amount = fee_amount
        if status:
            conversion.status = status
        if claim_signature:
            conversion.claim_signature = claim_signature

        conversion.updated_at = datetime_in_utcnow()
        self.session.commit()

        return ConversionFactory.conversion(row_id=conversion.row_id, id=conversion.id,
                                            wallet_pair_id=conversion.wallet_pair_id,
                                            deposit_amount=conversion.deposit_amount,
                                            claim_amount=conversion.claim_amount, fee_amount=conversion.fee_amount,
                                            status=conversion.status, claim_signature=conversion.claim_signature,
                                            created_by=conversion.created_by, created_at=conversion.created_at,
                                            updated_at=conversion.updated_at)

    @update_in_db()
    def update_conversion_transaction(self, conversion_transaction_id, status):
        conversion_transaction = self.session.query(ConversionTransactionDBModel) \
            .filter(ConversionTransactionDBModel.row_id == conversion_transaction_id).first()

        conversion_transaction.status = status
        conversion_transaction.updated_at = datetime_in_utcnow()
        self.session.commit()

    @read_from_db()
    def get_token_contract_address_for_conversion_id(self, conversion_id):
        contract_address = self.session.query(TokenPairDBModel.contract_address) \
            .join(WalletPairDBModel, WalletPairDBModel.token_pair_id == TokenPairDBModel.row_id) \
            .join(ConversionDBModel, ConversionDBModel.wallet_pair_id == WalletPairDBModel.row_id) \
            .filter(ConversionDBModel.id == conversion_id).first()

        if not contract_address:
            return None

        return contract_address[0]

    @read_from_db()
    def get_conversion_history_count(self, address):
        count = self.session.query(func.count(ConversionDBModel.id)) \
            .join(WalletPairDBModel, WalletPairDBModel.row_id == ConversionDBModel.wallet_pair_id) \
            .filter(
            or_(WalletPairDBModel.from_address == address, WalletPairDBModel.to_address == address)) \
            .first()

        return count[0]

    @read_from_db()
    def get_conversion_history(self, address, conversion_id, offset=0, limit=15):

        conversions_detail_query = self.session.query(ConversionDBModel) \
            .join(WalletPairDBModel, WalletPairDBModel.row_id == ConversionDBModel.wallet_pair_id) \
            .join(TokenPairDBModel, TokenPairDBModel.row_id == WalletPairDBModel.token_pair_id) \
            .order_by(case(
            [
                (
                    ConversionDBModel.status == ConversionStatus.WAITING_FOR_CLAIM.value,
                    1
                ),
                (
                    ConversionDBModel.status == ConversionStatus.USER_INITIATED.value, 2
                ),
                (
                    ConversionDBModel.status == ConversionStatus.CLAIM_INITIATED.value, 3
                ),
                (
                    ConversionDBModel.status == ConversionStatus.PROCESSING.value, 4
                ),
                (
                    ConversionDBModel.status == ConversionStatus.SUCCESS.value, 5
                ),
                (
                    ConversionDBModel.status == ConversionStatus.EXPIRED.value, 6
                )
            ],
            else_=7
        ).asc(), ConversionDBModel.created_at.desc())

        if address:
            conversions_detail_query = conversions_detail_query.filter(
                or_(WalletPairDBModel.from_address == address, WalletPairDBModel.to_address == address))

        if conversion_id:
            conversions_detail_query = conversions_detail_query.filter(ConversionDBModel.id == conversion_id)

        conversions_detail = conversions_detail_query.options(joinedload(ConversionDBModel.wallet_pair)).options(
            joinedload(ConversionDBModel.wallet_pair).joinedload(WalletPairDBModel.token_pair)).offset(offset).limit(
            limit).all()

        return [ConversionFactory.conversion_detail(conversion=conversion_detail) for conversion_detail in
                conversions_detail]

    @read_from_db()
    def get_transactions_for_conversion_row_ids(self, conversion_row_ids):
        transactions = self.session.query(TransactionDBModel) \
            .join(ConversionTransactionDBModel,
                  ConversionTransactionDBModel.row_id == TransactionDBModel.conversion_transaction_id) \
            .filter(ConversionTransactionDBModel.conversion_id.in_(conversion_row_ids),
                    ConversionTransactionDBModel.status != ConversionTransactionStatus.FAILED.value, ) \
            .order_by(TransactionDBModel.row_id, TransactionDBModel.created_at.asc()) \
            .options(joinedload(TransactionDBModel.token)) \
            .options(joinedload(TransactionDBModel.token).joinedload(TokenDBModel.blockchain_detail)) \
            .options(
            joinedload(TransactionDBModel.conversion_transaction).noload(ConversionTransactionDBModel.conversion)).all()

        return [ConversionFactory.transaction_detail(transaction=transaction) for transaction in transactions]

    @update_in_db()
    def update_transaction_by_id(self, tx_id, tx_operation, tx_visibility, tx_amount, confirmation, tx_status,
                                 created_by):
        transaction = self.session.query(TransactionDBModel) \
            .filter(TransactionDBModel.id == tx_id).one()
        if tx_operation:
            transaction.transaction_operation = tx_operation
        if tx_visibility:
            transaction.transaction_visibility = tx_visibility
        if tx_amount:
            transaction.transaction_amount = tx_amount
        if confirmation is not None:
            transaction.confirmation = confirmation
        if tx_status:
            transaction.status = tx_status
        if created_by:
            transaction.created_by = created_by
        transaction.updated_at = datetime_in_utcnow()
        self.session.commit()

    @read_from_db()
    def get_transaction_by_hash(self, tx_hash):
        transaction = self.session.query(TransactionDBModel) \
            .filter(TransactionDBModel.transaction_hash == tx_hash).first()

        if transaction is None:
            return None

        return ConversionFactory.transaction(row_id=transaction.row_id,
                                             id=transaction.id,
                                             conversion_transaction_id=transaction.conversion_transaction_id,
                                             token_id=transaction.token_id,
                                             transaction_visibility=transaction.transaction_visibility,
                                             transaction_operation=transaction.transaction_operation,
                                             transaction_hash=transaction.transaction_hash,
                                             transaction_amount=transaction.transaction_amount,
                                             confirmation=transaction.confirmation, status=transaction.status,
                                             created_by=transaction.created_by, created_at=transaction.created_at,
                                             updated_at=transaction.updated_at, conversion_transaction_obj=None,
                                             token_obj=None)

    @read_from_db()
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

    @read_from_db()
    def get_expiring_conversion(self, ethereum_expire_datetime, cardano_expire_datetime):
        from_token = aliased(TokenDBModel)
        to_token = aliased(TokenDBModel)
        from_blockchain = aliased(BlockChainDBModel)
        to_blockchain = aliased(BlockChainDBModel)

        conversions = self.session.query(ConversionDBModel.row_id, ConversionDBModel.id,
                                         ConversionDBModel.wallet_pair_id, ConversionDBModel.deposit_amount,
                                         ConversionDBModel.claim_amount, ConversionDBModel.fee_amount,
                                         ConversionDBModel.status, ConversionDBModel.claim_signature,
                                         ConversionDBModel.created_by, ConversionDBModel.created_at,
                                         ConversionDBModel.updated_at) \
            .join(WalletPairDBModel, WalletPairDBModel.row_id == ConversionDBModel.wallet_pair_id) \
            .join(TokenPairDBModel, TokenPairDBModel.row_id == WalletPairDBModel.token_pair_id) \
            .join(from_token, from_token.row_id == TokenPairDBModel.from_token_id) \
            .join(to_token, to_token.row_id == TokenPairDBModel.to_token_id) \
            .join(from_blockchain, from_blockchain.row_id == from_token.blockchain_id) \
            .join(to_blockchain, to_blockchain.row_id == to_token.blockchain_id) \
            .filter(ConversionDBModel.status == ConversionStatus.USER_INITIATED.value,
                    or_(and_(func.lower(from_blockchain.name) == BlockchainName.ETHEREUM.value.lower(),
                             ConversionDBModel.created_at <= str(ethereum_expire_datetime)),
                        and_(func.lower(from_blockchain.name) == BlockchainName.CARDANO.value.lower(),
                             ConversionDBModel.created_at <= str(cardano_expire_datetime)))).all()

        return [ConversionFactory.conversion(row_id=conversion.row_id, id=conversion.id,
                                             wallet_pair_id=conversion.wallet_pair_id,
                                             deposit_amount=conversion.deposit_amount,
                                             claim_amount=conversion.claim_amount, fee_amount=conversion.fee_amount,
                                             status=conversion.status, claim_signature=conversion.claim_signature,
                                             created_by=conversion.created_by, created_at=conversion.created_at,
                                             updated_at=conversion.updated_at) for conversion in conversions]

    @update_in_db()
    def set_conversions_to_expire(self, conversion_ids):
        self.session.query(ConversionDBModel) \
            .filter(ConversionDBModel.id.in_(conversion_ids)) \
            .update({ConversionDBModel.status: ConversionStatus.EXPIRED.value})

        self.session.commit()
