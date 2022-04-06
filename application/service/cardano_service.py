import json
import os
from decimal import Decimal
from http import HTTPStatus

import requests

from common.logger import get_logger
from constants.entity import CardanoAPIEntities
from constants.error_details import ErrorCode, ErrorDetails
from utils.exceptions import InternalServerErrorException

logger = get_logger(__name__)


class CardanoService:

    @staticmethod
    def get_deposit_address(token_name):
        logger.info(f"Getting the deposit address for the token={token_name}")
        base_path = os.getenv("CARDANO_SERVICE_BASE_PATH", None)
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value].value)
        try:
            response = requests.get(f"{base_path}/address/derive?token={token_name}", data=json.dumps({}),
                                    headers={"Content-Type": "application/json"})

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                                   error_details=ErrorDetails[
                                                       ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)

            response = json.loads(response.content.decode("utf-8"))
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano get deposit address={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)
        logger.info(f"Response={response}")
        return response

    @staticmethod
    def burn_token(conversion_id, address, token, tx_amount, tx_details, deposit_address_details):
        logger.info(
            f"Calling the burn token service on cardano with inputs as conversion_id={conversion_id}, "
            f"address={address}, {token}, tx_amount={tx_amount}, "
            f"tx_details={tx_details}, deposit_address_details={deposit_address_details}")

        base_path = os.getenv("CARDANO_SERVICE_BASE_PATH", None)
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.LAMBDA_ARN_BURN_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.LAMBDA_ARN_BURN_NOT_FOUND.value].value)
        try:
            payload = CardanoService.generate_payload_format(conversion_id=conversion_id, address=address,
                                                             tx_amount=str(Decimal(float(tx_amount))),
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
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano burn service={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)
        logger.info(f"Response={response}")

        return response

    @staticmethod
    def mint_token(conversion_id, address, token, tx_amount, tx_details, source_address):
        logger.info(
            f"Calling the mint token service on cardano with inputs as conversion_id={conversion_id}, "
            f"address={address}, token={token}, tx_amount={tx_amount}, tx_details={tx_details}, "
            f"source_address={source_address}")

        base_path = os.getenv("CARDANO_SERVICE_BASE_PATH", None)
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.LAMBDA_ARN_MINT_NOT_FOUND.value].value)

        try:
            payload = CardanoService.generate_payload_format(conversion_id=conversion_id, address=address,
                                                             tx_amount=str(Decimal(float(tx_amount))),
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
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano mint service={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value,
                                               error_details=ErrorDetails[
                                                   ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL.value].value)
        logger.info(f"Response={response}")
        return response

    @staticmethod
    def generate_transaction_detail(hash, environment):
        return {
            CardanoAPIEntities.HASH.value: hash,
            CardanoAPIEntities.ENVIRONMENT.value: environment
        }

    @staticmethod
    def generate_payload_format(conversion_id, address, tx_amount, tx_details):
        return {
            CardanoAPIEntities.CONVERSION_ID.value: conversion_id,
            CardanoAPIEntities.CARDANO_ADDRESS.value: address, CardanoAPIEntities.AMOUNT.value: tx_amount,
            CardanoAPIEntities.TRANSACTION_DETAILS.value: tx_details
        }
