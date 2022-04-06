import traceback

import boto3

from common.logger import get_logger
from config import QUEUE_DETAILS
from constants.entity import SQSEntities
from constants.error_details import ErrorCode, ErrorDetails
from utils.exceptions import InternalServerErrorException

logger = get_logger(__name__)


class SqsService:

    @staticmethod
    def send_message_to_queue(queue: str, message: str, message_group_id: str):
        payload = dict()
        queue_url = QUEUE_DETAILS.get(queue)
        if not queue_url:
            raise InternalServerErrorException(error_code=ErrorCode.QUEUE_DETAILS_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.QUEUE_DETAILS_NOT_FOUND.value].value)

        payload[SQSEntities.QUEUE_URL.value] = queue_url
        payload[SQSEntities.MESSAGE_BODY.value] = message
        if message_group_id:
            payload[SQSEntities.MESSAGE_GROUP_ID.value] = message_group_id

        logger.info(f"Started publishing the message to the queue with details={payload}")
        try:
            sqs_client = boto3.client('sqs')
            response = sqs_client.send_message(**payload)
            logger.info(response)
        except Exception as e:
            logger.error(f"Unable to send message because of {e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_SENDING_MESSAGE.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_SENDING_MESSAGE.value].value)
