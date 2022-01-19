import json
import unittest
from unittest.mock import patch

from application.handler.conversion_handlers import create_conversion_request
from infrastructure.models import TokenPairDBModel, ConversionFeeDBModel, TokenDBModel, BlockChainDBModel, \
    WalletPairDBModel, ConversionDBModel
from infrastructure.repositories.conversion_repository import ConversionRepository
from testcases.functional_testcases.test_variables import TestVariables

conversion_repo = ConversionRepository()
test_variables = TestVariables()


class TestConversion(unittest.TestCase):

    def setUp(self):
        self.tearDown()
        conversion_repo.session.add_all(test_variables.blockchain)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.token)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.conversion_fee)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.token_pair)
        conversion_repo.session.commit()

    @patch("common.utils.Utils.report_slack")
    def test_create_conversion_request(self, mock_report_slack):
        bad_request_body_missing = {'status': 'failed', 'data': None,
                                    'error': {'code': 'E0001', 'message': 'BAD_REQUEST', 'details': 'Missing body'}}
        bad_request_schema_not_matching = {'status': 'failed', 'data': None,
                                           'error': {'code': 'E0003', 'message': 'BAD_REQUEST',
                                                     'details': 'Schema is not matching with request'}}
        bad_request_property_value_empty = {'status': 'failed', 'data': None,
                                            'error': {'code': 'E0005', 'message': 'BAD_REQUEST',
                                                      'details': 'Property value is empty'}}
        bad_request_token_pair_id_not_exists = {'status': 'failed', 'data': None,
                                                'error': {'code': 1, 'message': 'BAD_REQUEST',
                                                          'details': 'Given toke pair id not exists'}}
        bad_request_incorrect_signature = {'status': 'failed', 'data': None, 'error': {'code': 'E0006', 'message': 'BAD_REQUEST', 'details': 'Incorrect signature provided'}}

        # Bad Request
        event = dict()
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_body_missing)

        body_input = json.dumps({})
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_schema_not_matching)

        body_input = json.dumps({
            "token_pair_id": "",
            "amount": "",
            "from_address": "",
            "to_address": "",
            "block_number": ""
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_schema_not_matching)

        body_input = json.dumps({
            "token_pair_id": "",
            "amount": "",
            "from_address": "",
            "to_address": "",
            "block_number": 0,
            "signature": ""
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_property_value_empty)

        body_input = json.dumps({
            "token_pair_id": "32477fd4ea994689a04646cbbaafd133",
            "amount": "1333.05",
            "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
            "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
            "block_number": 123456789,
            "signature": "0x2437d4833b185ff1458a21f45bce382f59dfc1d86c38fac53476615513ece5e174381cd44c1bcfe38a6ce30ba67b71dc37ca774d1c3d991ec5fcbf79dca568d81b"
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_token_pair_id_not_exists)

        body_input = json.dumps({
            "token_pair_id": "fdd6a416d8414154bcdd95f82b6ab239",
            "amount": "1333.05",
            "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
            "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
            "block_number": 123456789,
            "signature": "0x2437d4833b185ff1458a21f45bce382f59dfc1d86c38fac53476615513ece5e174381cd44c1bcfe38a6ce30ba67b71dc37ca774d1c3d991ec5fcbf79dca568d81b"
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_incorrect_signature)
        print("")

    def tearDown(self):
        conversion_repo.session.query(ConversionDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(WalletPairDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(TokenPairDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(ConversionFeeDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(TokenDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(BlockChainDBModel).delete()
        conversion_repo.session.commit()
