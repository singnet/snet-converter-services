from application.service.token_response import (
    get_all_token_pair_response,
    get_token_pair_internal_response,
    get_token_pair_response
)
from common.logger import get_logger
from infrastructure.repositories.token_repository import TokenRepository
from utils.general import get_response_from_entities

logger = get_logger(__name__)


class TokenService:

    def __init__(self):
        self.token_repo = TokenRepository()

    def get_all_token_pair(self):
        logger.info("Getting all token pair")
        token_pairs = self.token_repo.get_all_token_pair()
        return get_all_token_pair_response(get_response_from_entities(token_pairs))

    def get_token_pair(self, token_pair_id):
        logger.info(f"Getting the token pair for the given id={token_pair_id}")
        token_pair = self.token_repo.get_token_pair(token_pair_id=token_pair_id)
        return get_token_pair_response(token_pair.to_dict())

    def get_token_pair_internal(self, token_pair_id, token_pair_row_id=None):
        logger.info(f"Getting the token pair for the given id={token_pair_id} or token_pair_row_id={token_pair_row_id}")
        token_pair = self.token_repo.get_token_pair(token_pair_id=token_pair_id, token_pair_row_id=token_pair_row_id)
        return get_token_pair_internal_response(token_pair.to_dict())
