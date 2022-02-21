import traceback
import boto3

from common.logger import get_logger
from config import TOPIC_DETAILS
from constants.error_details import ErrorCode, ErrorDetails
from utils.exceptions import InternalServerErrorException

logger = get_logger(__name__)


class SnsService:

    @staticmethod
    def publish_message(topic: str, message: str):
        topic_arn = TOPIC_DETAILS.get(topic)
        if not topic_arn:
            raise InternalServerErrorException(error_code=ErrorCode.TOPIC_NOT_FOUND.value,
                                               error_details=ErrorDetails[ErrorCode.TOPIC_NOT_FOUND.value].value)

        logger.info(f"Started publishing the message to the topic_arn={topic_arn} with message={message}")
        try:
            sns_client = boto3.client('sns')
            response = sns_client.publish(
                TopicArn=topic_arn,
                Message=message
            )
            logger.info(response)
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Unable to publish because of {e}")
            raise e
