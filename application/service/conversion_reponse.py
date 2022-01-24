from constants.entity import ConversionEntities, WalletPairEntities


def get_latest_user_pending_conversion_request_response(conversion):
    return {
        ConversionEntities.ROW_ID.value: conversion[ConversionEntities.ROW_ID.value],
        ConversionEntities.ID.value: conversion[ConversionEntities.ID.value],
        ConversionEntities.WALLET_PAIR_ID.value: conversion[ConversionEntities.WALLET_PAIR_ID.value],
        ConversionEntities.DEPOSIT_AMOUNT.value: conversion[ConversionEntities.DEPOSIT_AMOUNT.value],
        ConversionEntities.STATUS.value: conversion[ConversionEntities.STATUS.value],
        ConversionEntities.UPDATED_AT.value: conversion[ConversionEntities.UPDATED_AT.value]
    }


def update_conversion_amount_response(conversion):
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
