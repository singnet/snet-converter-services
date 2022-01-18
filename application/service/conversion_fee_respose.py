from constants.entity import ConversionFeeEntities


def get_conversion_fee_response(conversion_fee):
    if not len(conversion_fee):
        return conversion_fee

    return {
        ConversionFeeEntities.ID.value: conversion_fee[ConversionFeeEntities.ID.value],
        ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value: conversion_fee[
            ConversionFeeEntities.PERCENTAGE_FROM_SOURCE.value],
        ConversionFeeEntities.UPDATED_AT.value: conversion_fee[ConversionFeeEntities.UPDATED_AT.value]
    }
