import traceback

import boto3

from common.logger import get_logger
from config import QUEUE_DETAILS
from constants.error_details import ErrorCode, ErrorDetails
from utils.exceptions import InternalServerErrorException

logger = get_logger(__name__)


class SqsService:

    @staticmethod
    def send_message_to_queue(queue: str, message: str, message_group_id: str):
        queue_url = QUEUE_DETAILS.get(queue)
        if not queue_url:
            raise InternalServerErrorException(error_code=ErrorCode.QUEUE_DETAILS_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.QUEUE_DETAILS_NOT_FOUND.value].value)

        logger.info(f"Started publishing the message to the queue_url={queue_url} with message={message}, "
                    f"message group id={message_group_id}")
        try:
            sqs_client = boto3.client('sqs')
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message,
                MessageGroupId=message_group_id
            )
            logger.info(response)
        except Exception as e:
            logger.error(f"Unable to send message because of {e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_SENDING_MESSAGE.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_SENDING_MESSAGE.value].value)
