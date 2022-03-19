import json
from enum import Enum

from common.boto_utils import BotoUtils
from common.logger import get_logger

logger = get_logger(__name__)


class BotoUtility:

    @staticmethod
    def invoke_lambda_as_api(lambda_function_arn, invocation_type, payload, success_code=200):
        response = BotoUtils.invoke_lambda(lambda_function_arn, invocation_type, payload)

        if "statusCode" not in response or response["statusCode"] != success_code:
            logger.error(response)
            raise Exception('Failed to call lambda')

        return json.loads(response['body'])['data']


class LambdaInvocationTypes(Enum):
    REQUEST_RESPONSE = 'RequestResponse'
