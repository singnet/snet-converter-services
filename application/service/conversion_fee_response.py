from application.service.blockchain_response import get_blockchain_for_token_response
from constants.entity import ConversionFeeEntities, TokenEntities


def get_conversion_fee_response(conversion_fee):
    if not len(conversion_fee):
        return conversion_fee

    return {
        ConversionFeeEntities.ID.value: conversion_fee[ConversionFeeEntities.ID.value],
        ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value: conversion_fee[
            ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value],
        ConversionFeeEntities.TOKEN.value: get_short_token_response(conversion_fee[
            ConversionFeeEntities.TOKEN.value]),
        ConversionFeeEntities.UPDATED_AT.value: conversion_fee[ConversionFeeEntities.UPDATED_AT.value]
    }


def get_short_token_response(token):
    return {
        TokenEntities.ID.value: token[TokenEntities.ID.value],
        TokenEntities.NAME.value: token[TokenEntities.NAME.value],
        TokenEntities.SYMBOL.value: token[TokenEntities.SYMBOL.value],
        TokenEntities.LOGO.value: token[TokenEntities.LOGO.value],
        TokenEntities.ALLOWED_DECIMAL.value: token[TokenEntities.ALLOWED_DECIMAL.value],
        TokenEntities.TOKEN_ADDRESS.value: token[TokenEntities.TOKEN_ADDRESS.value],
        TokenEntities.CONTRACT_ADDRESS.value: token[TokenEntities.CONTRACT_ADDRESS.value],
        TokenEntities.UPDATED_AT.value: token[TokenEntities.UPDATED_AT.value],
        TokenEntities.BLOCKCHAIN.value: get_blockchain_for_token_response(token[TokenEntities.BLOCKCHAIN.value])
    }
