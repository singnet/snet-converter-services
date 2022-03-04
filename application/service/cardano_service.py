import json
import requests
from decimal import Decimal
from http import HTTPStatus
from common.logger import get_logger
from config import CARDANO_SERVICE_API
from constants.entity import CardanoAPIEntities
from constants.error_details import ErrorCode, ErrorDetails
from utils.exceptions import InternalServerErrorException

logger = get_logger(__name__)


class CardanoService:

    @staticmethod
    def get_deposit_address():
        logger.info("Getting the deposit address")
        base_path = CARDANO_SERVICE_API['CARDANO_SERVICE_BASE_PATH']
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value].value)
        try:
            response = requests.post(f"{base_path}/address/derive", data=json.dumps({}),
                                     headers={"Content-Type": "application/json"})

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                                   error_details=ErrorDetails[
                                                       ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)

            response = json.loads(response.content.decode("utf-8"))
            logger.info(f"Response={response}")
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano get deposit address={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)

        if not response.get(CardanoAPIEntities.DERIVED_ADDRESS.value):
            raise InternalServerErrorException(error_code=ErrorCode.DERIVED_ADDRESS_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.DERIVED_ADDRESS_NOT_FOUND.value].value)

        return response.get(CardanoAPIEntities.DERIVED_ADDRESS.value)

    @staticmethod
    def burn_token(address, token, tx_amount, tx_details, deposit_address_details):
        logger.info(
            f"Calling the burn token service on cardano with inputs as address={address}, {token}, tx_amount={tx_amount}, "
            f"tx_details={tx_details}, deposit_address_details={deposit_address_details}")

        base_path = CARDANO_SERVICE_API['CARDANO_SERVICE_BASE_PATH']
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.LAMBDA_ARN_BURN_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.LAMBDA_ARN_BURN_NOT_FOUND.value].value)
        try:
            payload = CardanoService.generate_payload_format(address=address, tx_amount=str(Decimal(float(tx_amount))),
                                                             tx_details=tx_details)
            payload[CardanoAPIEntities.DEPOSIT_ADDRESS_DETAILS.value] = deposit_address_details
            logger.info(f"Payload for burning ={json.dumps(payload)}")
            response = requests.post(f"{base_path}/{token}/burn", data=json.dumps(payload),
                                     headers={"Content-Type": "application/json"})

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                                   error_details=ErrorDetails[
                                                       ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)
            response = json.loads(response.content.decode("utf-8"))
            logger.info(f"Response={response}")
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano burn service={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)

        tx_id = response.get(CardanoAPIEntities.TRANSACTION_ID.value)
        if not tx_id or not tx_id.strip():
            raise InternalServerErrorException(
                error_code=ErrorCode.TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API.value,
                error_details=ErrorDetails[
                    ErrorCode.TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API.value].value)
        return response

    @staticmethod
    def mint_token(address, token, tx_amount, tx_details, source_address):
        logger.info(
            f"Calling the mint token service on cardano with inputs as address={address}, token={token}, tx_amount={tx_amount}, tx_details={tx_details}, source_address={source_address}")

        base_path = CARDANO_SERVICE_API['CARDANO_SERVICE_BASE_PATH']
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value].value)

        try:
            payload = CardanoService.generate_payload_format(address=address, tx_amount=str(Decimal(float(tx_amount))),
                                                             tx_details=tx_details)
            payload[CardanoAPIEntities.SOURCE_ADDRESS.value] = source_address
            logger.info(f"Payload for minting = {json.dumps(payload)}")

            response = requests.post(f"{base_path}/{token}/mint", data=json.dumps(payload),
                                     headers={"Content-Type": "application/json"})

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                                   error_details=ErrorDetails[
                                                       ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)

            response = json.loads(response.content.decode("utf-8"))
            logger.info(f"Response={response}")
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano mint service={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)
        tx_id = response.get(CardanoAPIEntities.TRANSACTION_ID.value)
        if not tx_id or not tx_id.strip():
            raise InternalServerErrorException(
                error_code=ErrorCode.TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API.value,
                error_details=ErrorDetails[
                    ErrorCode.TRANSACTION_ID_NOT_PRESENT_IN_CARDANO_SERVICE_API.value].value)
        return response

    @staticmethod
    def generate_transaction_detail(hash, environment):
        return {
            CardanoAPIEntities.HASH.value: hash,
            CardanoAPIEntities.ENVIRONMENT.value: environment
        }

    @staticmethod
    def generate_payload_format(address, tx_amount, tx_details):
        return {
            CardanoAPIEntities.CARDANO_ADDRESS.value: address, CardanoAPIEntities.AMOUNT.value: tx_amount,
            CardanoAPIEntities.TRANSACTION_DETAILS.value: tx_details
        }
