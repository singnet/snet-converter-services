from domain.entities.conversion import Conversion
from domain.entities.conversion_detail import ConversionDetail
from domain.entities.transaction import Transaction
from domain.entities.transaction_conversion import ConversionTransaction
from domain.factory.token_factory import TokenFactory
from domain.factory.wallet_pair_factory import WalletPairFactory


class ConversionFactory:

    @staticmethod
    def conversion(row_id, id, wallet_pair_id, deposit_amount, status, claim_signature,
                   created_by, created_at, updated_at, claim_amount=None, fee_amount=None):
        return Conversion(row_id=row_id, id=id, wallet_pair_id=wallet_pair_id, deposit_amount=deposit_amount,
                          claim_amount=claim_amount, fee_amount=fee_amount, status=status,
                          claim_signature=claim_signature, created_by=created_by, created_at=created_at,
                          updated_at=updated_at)

    @staticmethod
    def transaction(row_id, id, conversion_transaction_id, token_id, transaction_visibility,
                    transaction_operation, transaction_hash, transaction_amount, confirmation, status, created_by,
                    created_at, updated_at, conversion_transaction_obj, token_obj):
        return Transaction(row_id=row_id, id=id, conversion_transaction_id=conversion_transaction_id,
                           token_id=token_id, transaction_visibility=transaction_visibility,
                           transaction_operation=transaction_operation, transaction_hash=transaction_hash,
                           transaction_amount=transaction_amount, confirmation=confirmation, status=status,
                           created_by=created_by, created_at=created_at, updated_at=updated_at,
                           conversion_transaction_obj=conversion_transaction_obj, token_obj=token_obj)

    @staticmethod
    def conversion_transaction(row_id, id, conversion_id, status, created_by, created_at, updated_at):
        return ConversionTransaction(row_id=row_id, id=id, conversion_id=conversion_id, status=status,
                                     created_by=created_by, created_at=created_at, updated_at=updated_at)

    @staticmethod
    def conversion_detail(conversion):
        wallet_pair = conversion.wallet_pair
        conversion_obj = ConversionFactory.conversion(row_id=conversion.row_id, id=conversion.id,
                                                      wallet_pair_id=conversion.wallet_pair_id,
                                                      deposit_amount=conversion.deposit_amount,
                                                      claim_amount=conversion.claim_amount,
                                                      fee_amount=conversion.fee_amount, status=conversion.status,
                                                      claim_signature=conversion.claim_signature,
                                                      created_by=conversion.created_by,
                                                      created_at=conversion.created_at,
                                                      updated_at=conversion.updated_at)
        wallet_pair_obj = WalletPairFactory.wallet_pair(row_id=wallet_pair.row_id, id=wallet_pair.id,
                                                        token_pair_id=wallet_pair.token_pair_id,
                                                        from_address=wallet_pair.from_address,
                                                        to_address=wallet_pair.to_address,
                                                        deposit_address=wallet_pair.deposit_address,
                                                        deposit_address_detail=wallet_pair.deposit_address_detail,
                                                        signature=wallet_pair.signature,
                                                        signature_metadata=wallet_pair.signature_metadata,
                                                        signature_expiry=wallet_pair.signature_expiry,
                                                        created_by=wallet_pair.created_by,
                                                        created_at=wallet_pair.created_at,
                                                        updated_at=wallet_pair.updated_at)
        token_pair = wallet_pair.token_pair
        from_token = token_pair.from_token
        from_blockchain = from_token.blockchain_detail

        from_token_obj = TokenFactory.token(row_id=from_token.row_id, id=from_token.id, name=from_token.name,
                                            description=from_token.description,
                                            symbol=from_token.symbol, logo=from_token.logo,
                                            allowed_decimal=from_token.allowed_decimal,
                                            token_address=from_token.token_address,
                                            created_by=from_token.created_by, created_at=from_token.created_at,
                                            updated_at=from_token.updated_at, blockchain_detail=from_blockchain)
        to_token = token_pair.to_token
        to_blockchain = to_token.blockchain_detail

        to_token_obj = TokenFactory.token(row_id=to_token.row_id, id=to_token.id, name=to_token.name,
                                          description=to_token.description,
                                          symbol=to_token.symbol, logo=to_token.logo,
                                          allowed_decimal=to_token.allowed_decimal,
                                          token_address=from_token.token_address,
                                          created_by=to_token.created_by, created_at=to_token.created_at,
                                          updated_at=to_token.updated_at, blockchain_detail=to_blockchain)

        return ConversionDetail(conversion_obj=conversion_obj, wallet_pair_obj=wallet_pair_obj,
                                from_token_obj=from_token_obj,
                                to_token_obj=to_token_obj)

    @staticmethod
    def transaction_detail(transaction):
        conversion_transaction_db_obj = transaction.conversion_transaction
        token_db_obj = transaction.token

        conversion_transaction_obj = ConversionFactory.conversion_transaction(
            row_id=conversion_transaction_db_obj.row_id, id=conversion_transaction_db_obj.id,
            conversion_id=conversion_transaction_db_obj.conversion_id, status=conversion_transaction_db_obj.status,
            created_by=conversion_transaction_db_obj.created_by,
            created_at=conversion_transaction_db_obj.created_at,
            updated_at=conversion_transaction_db_obj.updated_at)

        token_obj = TokenFactory.token(row_id=token_db_obj.row_id, id=token_db_obj.id, name=token_db_obj.name,
                                       description=token_db_obj.description,
                                       symbol=token_db_obj.symbol, logo=token_db_obj.logo,
                                       allowed_decimal=token_db_obj.allowed_decimal,
                                       token_address=token_db_obj.token_address,
                                       created_by=token_db_obj.created_by, created_at=token_db_obj.created_at,
                                       updated_at=token_db_obj.updated_at,
                                       blockchain_detail=token_db_obj.blockchain_detail)

        return ConversionFactory.transaction(row_id=transaction.row_id, id=transaction.id,
                                             conversion_transaction_id=transaction.conversion_transaction_id,
                                             token_id=transaction.token_id,
                                             transaction_visibility=transaction.transaction_visibility,
                                             transaction_operation=transaction.transaction_operation,
                                             transaction_hash=transaction.transaction_hash,
                                             transaction_amount=transaction.transaction_amount,
                                             confirmation=transaction.confirmation,
                                             status=transaction.status,
                                             created_by=transaction.created_by,
                                             created_at=transaction.created_at,
                                             updated_at=transaction.updated_at,
                                             conversion_transaction_obj=conversion_transaction_obj,
                                             token_obj=token_obj)
