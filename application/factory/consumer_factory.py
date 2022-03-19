import json

from common.logger import get_logger
from constants.entity import EventConsumerEntity, EthereumEventConsumerEntities, CardanoEventConsumer, \
    ConverterBridgeEntities
from constants.error_details import ErrorCode, ErrorDetails
from constants.general import BlockchainName
from utils.exceptions import InternalServerErrorException

logger = get_logger(__name__)


def convert_consumer_event(event):
    new_format = []
    name = event.get(EthereumEventConsumerEntities.NAME.value, None)
    data = event.get(EthereumEventConsumerEntities.DATA.value, None)
    records = event.get(CardanoEventConsumer.RECORDS.value, [])
    try:
        if name and data:
            new_format.append(consumer_required_format(blockchain_name=BlockchainName.ETHEREUM.value,
                                                       blockchain_event=event))
        elif records:
            for record in records:
                body = record.get(CardanoEventConsumer.BODY.value)
                if body:
                    parsed_body = json.loads(body)
                    message = parsed_body.get(CardanoEventConsumer.MESSAGE.value)
                    if message:
                        parsed_message = json.loads(message)
                        new_format.append(consumer_required_format(blockchain_name=BlockchainName.CARDANO.value,
                                                                   blockchain_event=parsed_message))
    except Exception as e:
        logger.info(f"Error while trying to parse the input={json.dumps(event)} with error of {e}")
        raise InternalServerErrorException(error_code=ErrorCode.UNABLE_TO_PARSE_THE_INPUT_EVENT.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNABLE_TO_PARSE_THE_INPUT_EVENT.value].value)
    return new_format


def consumer_required_format(blockchain_name, blockchain_event):
    return {
        EventConsumerEntity.BLOCKCHAIN_NAME.value: blockchain_name,
        EventConsumerEntity.BLOCKCHAIN_EVENT.value: blockchain_event
    }


def convert_converter_bridge_event(event):
    new_format = []
    records = event.get(ConverterBridgeEntities.RECORDS.value, [])
    try:
        for record in records:
            body = record.get(ConverterBridgeEntities.BODY.value)
            if body:
                parsed_body = json.loads(body)
                new_format.append(parsed_body)

    except Exception as e:
        logger.info(f"Error while trying to parse the input={json.dumps(event)} with error of {e}")
        raise InternalServerErrorException(error_code=ErrorCode.UNABLE_TO_PARSE_THE_INPUT_EVENT.value,
                                           error_details=ErrorDetails[
                                               ErrorCode.UNABLE_TO_PARSE_THE_INPUT_EVENT.value].value)
    return new_format
