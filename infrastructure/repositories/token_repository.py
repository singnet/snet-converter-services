from sqlalchemy.orm import joinedload

from constants.error_details import ErrorCode, ErrorDetails
from domain.factory.token_factory import TokenFactory
from infrastructure.models import TokenPairDBModel
from infrastructure.repositories.base_repository import BaseRepository
from utils.database import read_from_db
from utils.exceptions import TokenPairIdNotExitsException


class TokenRepository(BaseRepository):

    @read_from_db()
    def get_all_token_pair(self):
        token_pairs = self.session.query(TokenPairDBModel).filter(TokenPairDBModel.is_enabled.is_(True)) \
            .options(joinedload(TokenPairDBModel.from_token)).options(joinedload(TokenPairDBModel.to_token)) \
            .options(joinedload(TokenPairDBModel.conversion_fee)).all()
        return [TokenFactory.token_pair(row_id=token_pair.row_id, id_=token_pair.id, min_value=token_pair.min_value,
                                        max_value=token_pair.max_value, created_by=token_pair.created_by,
                                        created_at=token_pair.created_at, updated_at=token_pair.updated_at,
                                        from_token=token_pair.from_token, to_token=token_pair.to_token,
                                        conversion_fee=token_pair.conversion_fee,
                                        conversion_ratio=token_pair.conversion_ratio) for
                token_pair
                in token_pairs]

    @read_from_db()
    def get_token_pair(self, token_pair_id, token_pair_row_id=None):
        token_pair_query = self.session.query(TokenPairDBModel).filter(TokenPairDBModel.is_enabled.is_(True)) \
            .options(joinedload(TokenPairDBModel.from_token)).options(joinedload(TokenPairDBModel.to_token)) \
            .options(joinedload(TokenPairDBModel.conversion_fee))

        if token_pair_id:
            token_pair_query = token_pair_query.filter(TokenPairDBModel.id == token_pair_id)
        if token_pair_row_id:
            token_pair_query = token_pair_query.filter(TokenPairDBModel.row_id == token_pair_row_id)

        token_pair = token_pair_query.first()

        if token_pair is None:
            raise TokenPairIdNotExitsException(error_code=ErrorCode.TOKEN_PAIR_NOT_EXISTS.value,
                                               error_details=ErrorDetails[ErrorCode.TOKEN_PAIR_NOT_EXISTS.value].value)

        return TokenFactory.token_pair(row_id=token_pair.row_id, id_=token_pair.id, min_value=token_pair.min_value,
                                       max_value=token_pair.max_value, created_by=token_pair.created_by,
                                       created_at=token_pair.created_at, updated_at=token_pair.updated_at,
                                       from_token=token_pair.from_token, to_token=token_pair.to_token,
                                       conversion_fee=token_pair.conversion_fee,
                                       conversion_ratio=token_pair.conversion_ratio)
