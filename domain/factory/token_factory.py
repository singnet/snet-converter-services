from domain.entities.token import Token
from domain.entities.token_pair import TokenPair
from domain.factory.blockchain_factory import BlockchainFactory
from domain.factory.conversion_fee_factory import ConversionFeeFactory


class TokenFactory:

    @staticmethod
    def token(row_id, id_, name, description, symbol, logo, allowed_decimal, token_address, contract_address,
              created_by, created_at, updated_at, blockchain_detail):
        blockchain_obj = BlockchainFactory.blockchain(id=blockchain_detail.id, name=blockchain_detail.name,
                                                      description=blockchain_detail.description,
                                                      symbol=blockchain_detail.symbol,
                                                      logo=blockchain_detail.logo,
                                                      chain_id=blockchain_detail.chain_id,
                                                      block_confirmation=blockchain_detail.block_confirmation,
                                                      is_extension_available=blockchain_detail.is_extension_available,
                                                      created_by=blockchain_detail.created_by,
                                                      created_at=blockchain_detail.created_at,
                                                      updated_at=blockchain_detail.updated_at)

        return Token(row_id=row_id, id_=id_, name=name, description=description, symbol=symbol, logo=logo,
                     allowed_decimal=allowed_decimal, token_address=token_address, contract_address=contract_address,
                     created_by=created_by, created_at=created_at, updated_at=updated_at, blockchain_obj=blockchain_obj)

    @staticmethod
    def token_pair_detail(row_id, id_, min_value, max_value, created_by, created_at, updated_at, from_token_obj,
                          to_token_obj, conversion_fee_obj, conversion_ratio):
        return TokenPair(row_id=row_id, id_=id_, min_value=min_value, max_value=max_value, created_by=created_by,
                         created_at=created_at, updated_at=updated_at, from_token_obj=from_token_obj,
                         to_token_obj=to_token_obj, conversion_fee_obj=conversion_fee_obj,
                         conversion_ratio=conversion_ratio)

    @staticmethod
    def convert_token_db_object_to_object(token):
        return TokenFactory.token(row_id=token.row_id, id_=token.id, name=token.name, description=token.description,
                                  symbol=token.symbol, logo=token.logo, allowed_decimal=token.allowed_decimal,
                                  token_address=token.token_address, contract_address=token.contract_address,
                                  created_by=token.created_by, created_at=token.created_at, updated_at=token.updated_at,
                                  blockchain_detail=token.blockchain_detail)

    @staticmethod
    def token_pair(row_id, id_, min_value, max_value, created_by, created_at, updated_at, from_token,
                   to_token, conversion_fee, conversion_ratio):
        from_token_obj = TokenFactory.convert_token_db_object_to_object(from_token)
        to_token_obj = TokenFactory.convert_token_db_object_to_object(to_token)
        conversion_fee_obj = ConversionFeeFactory.convert_conversion_fee_db_object_to_object(conversion_fee)

        return TokenFactory.token_pair_detail(row_id=row_id, id_=id_, min_value=min_value, max_value=max_value,
                                              created_by=created_by, created_at=created_at, updated_at=updated_at,
                                              from_token_obj=from_token_obj, to_token_obj=to_token_obj,
                                              conversion_fee_obj=conversion_fee_obj, conversion_ratio=conversion_ratio)
