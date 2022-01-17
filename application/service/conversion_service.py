from common.logger import get_logger

logger = get_logger(__name__)


class ConversionService:

    def __init__(self):
        pass

    def create_conversion_request(self, token_pair_id, amount, from_address, to_address, block_number, signature):
        logger.info(f"Creating the conversion request for token_pair_id={token_pair_id}, amount={amount}, "
                    f"from_address={from_address}, to_address={to_address}, block_number={block_number}, "
                    f"signature={signature}")
        """
            TODO: validate the signature, address, get deposit address,     
        """
