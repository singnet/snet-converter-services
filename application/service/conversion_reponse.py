from constants.entity import ConversionEntities, WalletPairEntities, ConversionDetailEntities, TokenEntities, \
    BlockchainEntities, TransactionEntities, TransactionConversionEntities


def get_latest_user_pending_conversion_request_response(conversion):
    return {
        ConversionEntities.ROW_ID.value: conversion[ConversionEntities.ROW_ID.value],
        ConversionEntities.ID.value: conversion[ConversionEntities.ID.value],
        ConversionEntities.WALLET_PAIR_ID.value: conversion[ConversionEntities.WALLET_PAIR_ID.value],
        ConversionEntities.DEPOSIT_AMOUNT.value: conversion[ConversionEntities.DEPOSIT_AMOUNT.value],
        ConversionEntities.STATUS.value: conversion[ConversionEntities.STATUS.value],
        ConversionEntities.UPDATED_AT.value: conversion[ConversionEntities.UPDATED_AT.value]
    }


def create_conversion_response(conversion):
    return {
        ConversionEntities.ROW_ID.value: conversion[ConversionEntities.ROW_ID.value],
        ConversionEntities.ID.value: conversion[ConversionEntities.ID.value],
        ConversionEntities.WALLET_PAIR_ID.value: conversion[ConversionEntities.WALLET_PAIR_ID.value],
        ConversionEntities.DEPOSIT_AMOUNT.value: conversion[ConversionEntities.DEPOSIT_AMOUNT.value],
        ConversionEntities.STATUS.value: conversion[ConversionEntities.STATUS.value],
        ConversionEntities.UPDATED_AT.value: conversion[ConversionEntities.UPDATED_AT.value]
    }


def create_conversion_request_response(wallet_pair, conversion):
    return {
        ConversionEntities.ID.value: conversion[ConversionEntities.ID.value],
        WalletPairEntities.DEPOSIT_ADDRESS.value: wallet_pair[WalletPairEntities.DEPOSIT_ADDRESS.value]
    }


def get_conversion_detail_for_conversion_internal_response(conversion):
    return {
        ConversionEntities.ROW_ID.value: conversion[ConversionEntities.ROW_ID.value],
        ConversionEntities.ID.value: conversion[ConversionEntities.ID.value],
        ConversionEntities.DEPOSIT_AMOUNT.value: conversion[ConversionEntities.DEPOSIT_AMOUNT.value],
        ConversionEntities.CLAIM_AMOUNT.value: conversion[ConversionEntities.CLAIM_AMOUNT.value],
        ConversionEntities.FEE_AMOUNT.value: conversion[ConversionEntities.FEE_AMOUNT.value],
        ConversionEntities.STATUS.value: conversion[ConversionEntities.STATUS.value],
        ConversionEntities.UPDATED_AT.value: conversion[ConversionEntities.UPDATED_AT.value]
    }


def get_wallet_pair_response(wallet_pair):
    return {
        WalletPairEntities.FROM_ADDRESS.value: wallet_pair[WalletPairEntities.FROM_ADDRESS.value],
        WalletPairEntities.TO_ADDRESS.value: wallet_pair[WalletPairEntities.TO_ADDRESS.value],
    }


def get_blockchain_response(blockchain):
    return {
        BlockchainEntities.NAME.value: blockchain[BlockchainEntities.NAME.value],
        BlockchainEntities.SYMBOL.value: blockchain[BlockchainEntities.SYMBOL.value],
        BlockchainEntities.CHAIN_ID.value: blockchain[BlockchainEntities.CHAIN_ID.value]
    }


def get_token_response(token):
    return {
        TokenEntities.NAME.value: token[TokenEntities.NAME.value],
        TokenEntities.SYMBOL.value: token[TokenEntities.SYMBOL.value],
        TokenEntities.BLOCKCHAIN.value: get_blockchain_response(
            token[TokenEntities.BLOCKCHAIN.value])
    }


def get_token_internal_response(token):
    return {
        TokenEntities.ROW_ID.value: token[TokenEntities.ROW_ID.value],
        TokenEntities.NAME.value: token[TokenEntities.NAME.value],
        TokenEntities.SYMBOL.value: token[TokenEntities.SYMBOL.value],
        TokenEntities.BLOCKCHAIN.value: get_blockchain_response(
            token[TokenEntities.BLOCKCHAIN.value])
    }


def get_transaction_response(transactions):
    return [{
        TransactionEntities.ID.value: transaction[TransactionEntities.ID.value],
        TransactionEntities.TRANSACTION_OPERATION.value: transaction[TransactionEntities.TRANSACTION_OPERATION.value],
        TransactionEntities.TRANSACTION_HASH.value: transaction[TransactionEntities.TRANSACTION_HASH.value],
        TransactionEntities.TRANSACTION_AMOUNT.value: transaction[TransactionEntities.TRANSACTION_AMOUNT.value],
        TransactionEntities.STATUS.value: transaction[TransactionEntities.STATUS.value],
        TransactionEntities.UPDATED_AT.value: transaction[TransactionEntities.UPDATED_AT.value]
    } for transaction in transactions]


def get_transaction_internal_response(transactions):
    return [{
        TransactionEntities.ID.value: transaction[TransactionEntities.ID.value],
        TransactionEntities.CONVERSION_TRANSACTION_ID.value: transaction[
            TransactionEntities.CONVERSION_TRANSACTION_ID.value],
        TransactionEntities.TRANSACTION_OPERATION.value: transaction[TransactionEntities.TRANSACTION_OPERATION.value],
        TransactionEntities.TRANSACTION_HASH.value: transaction[TransactionEntities.TRANSACTION_HASH.value],
        TransactionEntities.TRANSACTION_AMOUNT.value: transaction[TransactionEntities.TRANSACTION_AMOUNT.value],
        TransactionEntities.STATUS.value: transaction[TransactionEntities.STATUS.value],
        TransactionEntities.UPDATED_AT.value: transaction[TransactionEntities.UPDATED_AT.value]
    } for transaction in transactions]


def get_conversion_detail_response(conversion_detail):
    return {
        ConversionDetailEntities.CONVERSION.value: get_conversion_detail_for_conversion_internal_response(
            conversion_detail[ConversionDetailEntities.CONVERSION.value]),
        ConversionDetailEntities.WALLET_PAIR.value: get_wallet_pair_response(
            conversion_detail[ConversionDetailEntities.WALLET_PAIR.value]),
        ConversionDetailEntities.FROM_TOKEN.value: get_token_internal_response(
            conversion_detail[ConversionDetailEntities.FROM_TOKEN.value]),
        ConversionDetailEntities.TO_TOKEN.value: get_token_internal_response(
            conversion_detail[ConversionDetailEntities.TO_TOKEN.value]),
        ConversionDetailEntities.TRANSACTIONS.value: get_transaction_internal_response(
            conversion_detail[ConversionDetailEntities.TRANSACTIONS.value])
    }


def get_conversion_history_for_conversion_response(conversion):
    return {
        ConversionEntities.ID.value: conversion[ConversionEntities.ID.value],
        ConversionEntities.DEPOSIT_AMOUNT.value: conversion[ConversionEntities.DEPOSIT_AMOUNT.value],
        ConversionEntities.CLAIM_AMOUNT.value: conversion[ConversionEntities.CLAIM_AMOUNT.value],
        ConversionEntities.FEE_AMOUNT.value: conversion[ConversionEntities.FEE_AMOUNT.value],
        ConversionEntities.STATUS.value: conversion[ConversionEntities.STATUS.value],
        ConversionEntities.UPDATED_AT.value: conversion[ConversionEntities.UPDATED_AT.value]
    }


def get_conversion_history_response(history):
    return [{
        ConversionDetailEntities.CONVERSION.value: get_conversion_history_for_conversion_response(
            conversion[ConversionDetailEntities.CONVERSION.value]),
        ConversionDetailEntities.WALLET_PAIR.value: get_wallet_pair_response(
            conversion[ConversionDetailEntities.WALLET_PAIR.value]),
        ConversionDetailEntities.FROM_TOKEN.value: get_token_response(
            conversion[ConversionDetailEntities.FROM_TOKEN.value]),
        ConversionDetailEntities.TO_TOKEN.value: get_token_response(
            conversion[ConversionDetailEntities.TO_TOKEN.value]),
        ConversionDetailEntities.TRANSACTIONS.value: get_transaction_response(
            conversion[ConversionDetailEntities.TRANSACTIONS.value])
    } for conversion in history]


def create_transaction_for_conversion_response(transaction):
    return {
        TransactionConversionEntities.ID.value: transaction[TransactionConversionEntities.ID.value],
    }


def create_conversion_transaction_response(conversion_transaction):
    return {
        TransactionConversionEntities.ROW_ID.value: conversion_transaction[TransactionConversionEntities.ROW_ID.value],
        TransactionConversionEntities.ID.value: conversion_transaction[TransactionConversionEntities.ID.value],
        TransactionConversionEntities.CONVERSION_ID.value: conversion_transaction[
            TransactionConversionEntities.CONVERSION_ID.value],
        TransactionConversionEntities.STATUS.value: conversion_transaction[TransactionConversionEntities.STATUS.value],
        TransactionConversionEntities.UPDATED_AT.value: conversion_transaction[
            TransactionConversionEntities.UPDATED_AT.value],
    }


def create_transaction_response(transaction):
    return {
        TransactionEntities.ID.value: transaction[TransactionEntities.ID.value]
    }
