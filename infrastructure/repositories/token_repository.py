from domain.factory.token_factory import TokenFactory
from infrastructure.models import TokenPairDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.exceptions import TokenPairIdNotExitsException


class TokenRepository(BaseRepository):
    def __init__(self):
        super().__init__()

    def get_all_token_pair(self):
        token_pairs = self.session.query(TokenPairDBModel).filter(TokenPairDBModel.is_enabled == True).all()
        return [TokenFactory.token_pair(id=token_pair.id, min_value=token_pair.min_value,
                                        max_value=token_pair.max_value, contract_address=token_pair.contract_address,
                                        created_by=token_pair.created_by, created_at=token_pair.created_at,
                                        updated_at=token_pair.updated_at, from_token=token_pair.from_token,
                                        to_token=token_pair.to_token, conversion_fee=token_pair.conversion_fee) for
                token_pair
                in token_pairs]

    def get_token_pair(self, token_pair_id):
        token_pair = self.session.query(TokenPairDBModel).filter(TokenPairDBModel.is_enabled == True,
                                                                 TokenPairDBModel.id == token_pair_id).first()

        if token_pair is None:
            raise TokenPairIdNotExitsException(error_code=1, error_details="Given toke pair id not exists")

        return TokenFactory.token_pair(id=token_pair.id, min_value=token_pair.min_value,
                                       max_value=token_pair.max_value, contract_address=token_pair.contract_address,
                                       created_by=token_pair.created_by, created_at=token_pair.created_at,
                                       updated_at=token_pair.updated_at, from_token=token_pair.from_token,
                                       to_token=token_pair.to_token, conversion_fee=token_pair.conversion_fee)
