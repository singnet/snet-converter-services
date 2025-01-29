from application.service.blockchain_response import get_blockchain_for_token_response
from application.service.conversion_fee_respose import get_conversion_fee_response
from constants.entity import TokenPairEntities, TokenEntities, TradingViewEntities


def get_trading_view_response(trading_view):
    return {
        TradingViewEntities.SYMBOL.value: trading_view[TradingViewEntities.SYMBOL.value],
        TradingViewEntities.ALT_TEXT.value: trading_view[TradingViewEntities.ALT_TEXT.value]
    }


def get_token_response(token):
    return {
        TokenEntities.ID.value: token[TokenEntities.ID.value],
        TokenEntities.NAME.value: token[TokenEntities.NAME.value],
        TokenEntities.SYMBOL.value: token[TokenEntities.SYMBOL.value],
        TokenEntities.LOGO.value: token[TokenEntities.LOGO.value],
        TokenEntities.ALLOWED_DECIMAL.value: token[TokenEntities.ALLOWED_DECIMAL.value],
        TokenEntities.TOKEN_ADDRESS.value: token[TokenEntities.TOKEN_ADDRESS.value],
        TokenEntities.CONTRACT_ADDRESS.value: token[TokenEntities.CONTRACT_ADDRESS.value],
        TokenEntities.UPDATED_AT.value: token[TokenEntities.UPDATED_AT.value],
        TokenEntities.BLOCKCHAIN.value: get_blockchain_for_token_response(token[TokenEntities.BLOCKCHAIN.value]),
        TokenEntities.TRADING_VIEW.value: get_trading_view_response(token[TokenEntities.TRADING_VIEW.value])
    }


def get_all_token_pair_response(token_pairs):
    return [{
        TokenPairEntities.ID.value: token_pair[TokenPairEntities.ID.value],
        TokenPairEntities.MIN_VALUE.value: token_pair[TokenPairEntities.MIN_VALUE.value],
        TokenPairEntities.MAX_VALUE.value: token_pair[TokenPairEntities.MAX_VALUE.value],
        TokenPairEntities.CONVERSION_RATIO.value: token_pair[TokenPairEntities.CONVERSION_RATIO.value],
        TokenPairEntities.FROM_TOKEN.value: get_token_response(token_pair[TokenPairEntities.FROM_TOKEN.value]),
        TokenPairEntities.TO_TOKEN.value: get_token_response(token_pair[TokenPairEntities.TO_TOKEN.value]),
        TokenPairEntities.IS_LIQUID.value: token_pair[TokenPairEntities.IS_LIQUID.value],
        TokenPairEntities.CONVERSION_FEE.value: get_conversion_fee_response(
            token_pair[TokenPairEntities.CONVERSION_FEE.value]),
        TokenPairEntities.UPDATED_AT.value: token_pair[TokenPairEntities.UPDATED_AT.value]
    } for token_pair in token_pairs]


def get_token_pair_response(token_pair):
    return {
        TokenPairEntities.ID.value: token_pair[TokenPairEntities.ID.value],
        TokenPairEntities.MIN_VALUE.value: token_pair[TokenPairEntities.MIN_VALUE.value],
        TokenPairEntities.MAX_VALUE.value: token_pair[TokenPairEntities.MAX_VALUE.value],
        TokenPairEntities.CONVERSION_RATIO.value: token_pair[TokenPairEntities.CONVERSION_RATIO.value],
        TokenPairEntities.FROM_TOKEN.value: get_token_response(token_pair[TokenPairEntities.FROM_TOKEN.value]),
        TokenPairEntities.TO_TOKEN.value: get_token_response(token_pair[TokenPairEntities.TO_TOKEN.value]),
        TokenPairEntities.IS_LIQUID.value: token_pair[TokenPairEntities.IS_LIQUID.value],
        TokenPairEntities.CONVERSION_FEE.value: get_conversion_fee_response(
            token_pair[TokenPairEntities.CONVERSION_FEE.value]),
        TokenPairEntities.UPDATED_AT.value: token_pair[TokenPairEntities.UPDATED_AT.value]
    }


def get_token_pair_internal_response(token_pair):
    return {
        TokenPairEntities.ROW_ID.value: token_pair[TokenPairEntities.ROW_ID.value],
        TokenPairEntities.ID.value: token_pair[TokenPairEntities.ID.value],
        TokenPairEntities.MIN_VALUE.value: token_pair[TokenPairEntities.MIN_VALUE.value],
        TokenPairEntities.MAX_VALUE.value: token_pair[TokenPairEntities.MAX_VALUE.value],
        TokenPairEntities.CONVERSION_RATIO.value: token_pair[TokenPairEntities.CONVERSION_RATIO.value],
        TokenPairEntities.FROM_TOKEN.value: get_token_response(token_pair[TokenPairEntities.FROM_TOKEN.value]),
        TokenPairEntities.TO_TOKEN.value: get_token_response(token_pair[TokenPairEntities.TO_TOKEN.value]),
        TokenPairEntities.IS_LIQUID.value: token_pair[TokenPairEntities.IS_LIQUID.value],
        TokenPairEntities.ADA_THRESHOLD.value: token_pair[TokenPairEntities.ADA_THRESHOLD.value],
        TokenPairEntities.CONVERSION_FEE.value: get_conversion_fee_response(
            token_pair[TokenPairEntities.CONVERSION_FEE.value]),
        TokenPairEntities.UPDATED_AT.value: token_pair[TokenPairEntities.UPDATED_AT.value]
    }
