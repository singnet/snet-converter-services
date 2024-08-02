import json
import os
from decimal import Decimal
from http import HTTPStatus

import requests

from common.logger import get_logger
from constants.entity import CardanoAPIEntities
from constants.error_details import ErrorCode
from utils.exceptions import InternalServerErrorException, BadRequestException
from application.service.wallet_pair_service import get_all_deposit_address_response

logger = get_logger(__name__)


class CardanoService:

    @staticmethod
    def get_deposit_address(token_name):
        logger.info(f"Getting the deposit address for the token={token_name}")
        base_path = os.getenv("CARDANO_SERVICE_BASE_PATH", None)
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.CARDANO_SERVICE_BASE_PATH_NOT_FOUND)
        try:
            response = requests.get(f"{base_path}/address/derive?token={token_name}", data=json.dumps({}),
                                    headers={"Content-Type": "application/json"})

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)

            response = json.loads(response.content.decode("utf-8"))
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano get deposit address={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)
        logger.info(f"Response={response}")
        return response

    @staticmethod
    def get_liquidity_addresses():
        logger.info(f"Getting the liquidity addresses")
        base_path = os.getenv("CARDANO_SERVICE_BASE_PATH", None)
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.CARDANO_SERVICE_BASE_PATH_NOT_FOUND)
        try:
            data = requests.get(f"{base_path}/cardano/liquidity/addresses", data=json.dumps({}),
                                    headers={"Content-Type": "application/json"})

            if data.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)

            prepare_response = json.loads(data.content.decode("utf-8"))

            response = get_all_deposit_address_response(prepare_response.get("data").get("liquidityAddresses"))

        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano get liquidity addresses={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)
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
            raise InternalServerErrorException(error_code=ErrorCode.CARDANO_SERVICE_BASE_PATH_NOT_FOUND)
        try:
            payload = CardanoService.generate_payload_format(conversion_id=conversion_id, address=address,
                                                             tx_amount=str(int(Decimal(tx_amount))),
                                                             tx_details=tx_details)
            payload[CardanoAPIEntities.DEPOSIT_ADDRESS_DETAILS.value] = deposit_address_details
            logger.info(f"Payload for burning ={json.dumps(payload)}")
            response = requests.post(f"{base_path}/{token}/burn", data=json.dumps(payload),
                                     headers={"Content-Type": "application/json"})

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)
            response = json.loads(response.content.decode("utf-8"))
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano burn service={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)
        logger.info(f"Response={response}")

        return response

    @staticmethod
    def mint_token(conversion_id, address, token, tx_amount, tx_details, source_address, fee, decimals_difference):
        logger.info(f"Calling the mint token service on cardano with inputs as conversion_id={conversion_id}, "
                    f"address={address}, token={token}, tx_amount={tx_amount}, tx_details={tx_details}, "
                    f"source_address={source_address}")

        base_path = os.getenv("CARDANO_SERVICE_BASE_PATH", None)
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.CARDANO_SERVICE_BASE_PATH_NOT_FOUND)

        try:
            payload = CardanoService.generate_payload_format(conversion_id=conversion_id,
                                                             address=address,
                                                             tx_amount=str(int(Decimal(tx_amount))),
                                                             tx_details=tx_details,
                                                             fee=str(int(Decimal(fee))),
                                                             decimals_difference=decimals_difference)
            payload[CardanoAPIEntities.SOURCE_ADDRESS.value] = source_address
            logger.info(f"Payload for minting = {json.dumps(payload)}")

            response = requests.post(f"{base_path}/{token}/mint", data=json.dumps(payload),
                                     headers={"Content-Type": "application/json"})

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)

            response = json.loads(response.content.decode("utf-8"))
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano mint service={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)
        logger.info(f"Response={response}")
        return response

    @staticmethod
    def liquidity_token_transfer(conversion_id, address, token, tx_amount, tx_details, source_address,
                                 conversion_ratio, burnt_token):
        logger.info(f"Calling the liquidity token transfer service on cardano with inputs as "
                    f"conversion_id={conversion_id}, address={address}, token={token}, tx_amount={tx_amount}, "
                    f"tx_details={tx_details}, source_address={source_address}, burnt_token={burnt_token}")

        base_path = os.getenv("CARDANO_SERVICE_BASE_PATH", None)
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.CARDANO_SERVICE_BASE_PATH_NOT_FOUND)

        try:
            payload = CardanoService.generate_payload_format(conversion_id=conversion_id,
                                                             address=address,
                                                             tx_amount=str(int(Decimal(tx_amount))),
                                                             tx_details=tx_details,
                                                             conversion_ratio=conversion_ratio)
            payload[CardanoAPIEntities.SOURCE_ADDRESS.value] = source_address
            payload[CardanoAPIEntities.BURNT_TOKEN.value] = burnt_token

            logger.info(f"Payload for liquidity token transfer = {json.dumps(payload)}")

            response = requests.post(f"{base_path}/{token}/liquidity/transfer", data=json.dumps(payload),
                                     headers={"Content-Type": "application/json"})

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)

            response = json.loads(response.content.decode("utf-8"))
        except Exception as e:
            logger.exception(f"Unexpected error while calling the liquidity token transfer service={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)
        logger.info(f"Response={response}")
        return response

    @staticmethod
    def get_token_liquidity(token_name):
        logger.info(f"Getting the token liquidity for the token={token_name}")
        base_path = os.getenv("CARDANO_SERVICE_BASE_PATH", None)
        if not base_path:
            raise InternalServerErrorException(error_code=ErrorCode.CARDANO_SERVICE_BASE_PATH_NOT_FOUND)
        try:
            response = requests.get(f"{base_path}/{token_name}/liquidity")

            if response.status_code == HTTPStatus.NOT_FOUND.value:
                raise BadRequestException(error_code=ErrorCode.NOT_LIQUID_CONTRACT)

            if response.status_code != HTTPStatus.OK.value:
                raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)

            response = json.loads(response.content.decode("utf-8"))
        except BadRequestException as bre:
            raise bre
        except Exception as e:
            logger.exception(f"Unexpected error while calling the cardano get token_liquidity={e}")
            raise InternalServerErrorException(error_code=ErrorCode.UNEXPECTED_ERROR_ON_CARDANO_SERVICE_CALL)
        logger.info(f"Response={response}")
        return response

    @staticmethod
    def generate_transaction_detail(hash, environment):
        return {
            CardanoAPIEntities.HASH.value: hash,
            CardanoAPIEntities.ENVIRONMENT.value: environment
        }

    @staticmethod
    def generate_payload_format(conversion_id, address, tx_amount, tx_details, fee=None, decimals_difference=None,
                                conversion_ratio=None):
        payload = {
            CardanoAPIEntities.CONVERSION_ID.value: conversion_id,
            CardanoAPIEntities.CARDANO_ADDRESS.value: address,
            CardanoAPIEntities.AMOUNT.value: tx_amount,
            CardanoAPIEntities.TRANSACTION_DETAILS.value: tx_details
        }
        if fee is not None:
            payload[CardanoAPIEntities.FEE.value] = fee
        if decimals_difference is not None:
            payload[CardanoAPIEntities.DECIMALS_DIFFERENCE.value] = decimals_difference
        if conversion_ratio is not None:
            payload[CardanoAPIEntities.CONVERSION_RATIO.value] = conversion_ratio
        return payload
