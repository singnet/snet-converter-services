@exception_handler(SLACK_HOOK=SLACK_HOOK, logger=logger)
def get_token_pair(event, context):
    logger.info(f"Got Airdrops Window Claims Events {event}")
    return generate_lambda_response(
        status.value,
        status.phrase,
        response,
        cors_enabled=True,
    )