from common.exception_handler import exception_handler


@exception_handler(SLACK_HOOK=SLACK_HOOK, logger=logger)
def create_conversion_request(event, context):
    logger.info(f"Got Airdrops Window Claims Events {event}")
    return generate_lambda_response(
        status.value,
        status.phrase,
        response,
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_conversion_history(event, context):
    logger.info(f"Got Airdrops Window Claims Events {event}")
    return generate_lambda_response(
        status.value,
        status.phrase,
        response,
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, logger=logger)
def update_transaction_hash(event, context):
    logger.info(f"Got Airdrops Window Claims Events {event}")
    return generate_lambda_response(
        status.value,
        status.phrase,
        response,
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, logger=logger)
def claim_conversion(event, context):
    logger.info(f"Got Airdrops Window Claims Events {event}")
    return generate_lambda_response(
        status.value,
        status.phrase,
        response,
        cors_enabled=True,
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_conversion(event, context):
    logger.info(f"Got Airdrops Window Claims Events {event}")
    return generate_lambda_response(
        status.value,
        status.phrase,
        response,
        cors_enabled=True,
    )