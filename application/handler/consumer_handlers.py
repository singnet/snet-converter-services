import json
import sys

sys.path.append('/opt')

from application.factory.consumer_factory import convert_consumer_event, convert_converter_bridge_event
from application.service.consumer_service import ConsumerService
from common.logger import get_logger
from config import SLACK_HOOK
from utils.exception_handler import exception_handler
from utils.exceptions import EXCEPTIONS

consumer_service = ConsumerService()

logger = get_logger(__name__)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def converter_event_consumer(event, context):
    logger.debug(f"Confirm and trigger transaction process request event={json.dumps(event)}")
    new_format = convert_consumer_event(event=event)
    for event in new_format:
        consumer_service.converter_event_consumer(payload=event)


@exception_handler(EXCEPTIONS=EXCEPTIONS, SLACK_HOOK=SLACK_HOOK, logger=logger)
def converter_bridge(event, context):
    logger.debug(f"Converter bridge request event={json.dumps(event)}")
    new_format = convert_converter_bridge_event(event=event)
    for event in new_format:
        consumer_service.converter_bridge(payload=event)
