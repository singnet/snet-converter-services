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
    def transaction(row_id, id, conversion_transaction_id, from_token_id, to_token_id, transaction_visibility,
                    transaction_operation, transaction_hash, transaction_amount, status, created_by, created_at,
                    updated_at):
        return Transaction(row_id=row_id, id=id, conversion_transaction_id=conversion_transaction_id,
                           from_token_id=from_token_id, to_token_id=to_token_id,
                           transaction_visibility=transaction_visibility, transaction_operation=transaction_operation,
                           transaction_hash=transaction_hash, transaction_amount=transaction_amount, status=status,
                           created_by=created_by, created_at=created_at, updated_at=updated_at)

    @staticmethod
    def conversion_transaction(row_id, id, conversion_id, status, created_by, created_at, updated_at):
        return ConversionTransaction(row_id=row_id, id=id, conversion_id=conversion_id, status=status,
                                     created_by=created_by, created_at=created_at, updated_at=updated_at)

    @staticmethod
    def convert_transaction_by_conversion_id(transaction_details):
        transaction_by_conversion_id = dict()
        for transaction_detail in transaction_details:
            conversion_id = transaction_detail.id
            transaction_by_conversion_id[conversion_id] = transaction_by_conversion_id.get(conversion_id, {})
            transaction_by_conversion_id[conversion_id]["conversion_id"] = conversion_id
            transaction_by_conversion_id[conversion_id]["transactions"] = transaction_by_conversion_id[
                conversion_id].get('transactions', [])
            transaction_by_conversion_id[conversion_id]["transactions"].append(
                transaction_detail.TransactionDBModel)

        return transaction_by_conversion_id

    @staticmethod
    def conversion_detail(conversion, wallet_pair, from_token, to_token, from_blockchain, to_blockchain, transactions):
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
                                                        signature=wallet_pair.signature,
                                                        signature_metadata=wallet_pair.signature_metadata,
                                                        signature_expiry=wallet_pair.signature_expiry,
                                                        created_by=wallet_pair.created_by,
                                                        created_at=wallet_pair.created_at,
                                                        updated_at=wallet_pair.updated_at)

        from_token_obj = TokenFactory.token(row_id=from_token.row_id, id=from_token.id, name=from_token.name,
                                            description=from_token.description,
                                            symbol=from_token.symbol, logo=from_token.logo,
                                            allowed_decimal=from_token.allowed_decimal,
                                            created_by=from_token.created_by, created_at=from_token.created_at,
                                            updated_at=from_token.updated_at, blockchain_detail=from_blockchain)
        to_token_obj = TokenFactory.token(row_id=to_token.row_id, id=to_token.id, name=to_token.name,
                                          description=to_token.description,
                                          symbol=to_token.symbol, logo=to_token.logo,
                                          allowed_decimal=to_token.allowed_decimal, created_by=to_token.created_by,
                                          created_at=to_token.created_at,
                                          updated_at=to_token.updated_at, blockchain_detail=to_blockchain)

        transactions = transactions.get("transactions", [])
        transaction_objs = [ConversionFactory.transaction(row_id=transaction.row_id, id=transaction.id,
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
                                                          updated_at=transaction.updated_at) for transaction in
                            transactions]
        return ConversionDetail(conversion_obj=conversion_obj, wallet_pair_obj=wallet_pair_obj,
                                from_token_obj=from_token_obj,
                                to_token_obj=to_token_obj, transaction_objs=transaction_objs)

    @staticmethod
    def get_conversion_ids(conversions_detail):
        conversion_ids = list()
        for conversion_detail in conversions_detail:
            conversion = conversion_detail[0]
            conversion_ids.append(conversion.id)

        return set(conversion_ids)
