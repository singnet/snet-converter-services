import json
import unittest
from unittest.mock import patch

from sqlalchemy import distinct

from application.handler.conversion_handlers import create_conversion_request, get_conversion_history
from infrastructure.models import TokenPairDBModel, ConversionFeeDBModel, TokenDBModel, BlockChainDBModel, \
    WalletPairDBModel, ConversionDBModel, TransactionDBModel, ConversionTransactionDBModel
from infrastructure.repositories.conversion_repository import ConversionRepository
from testcases.functional_testcases.test_variables import TestVariables

test_variables = TestVariables()
conversion_repo = ConversionRepository()


class TestConversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conversion_repo.session.query(TransactionDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(ConversionTransactionDBModel).delete()
        conversion_repo.session.commit()
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

    def setUp(self):
        conversion_repo.session.add_all(test_variables.blockchain)
        conversion_repo.session.add_all(test_variables.token)
        conversion_repo.session.commit()
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.conversion_fee)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.token_pair)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.wallet_pair)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.conversion)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.conversion_transaction)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(test_variables.transaction)
        conversion_repo.session.commit()

    @patch("common.utils.Utils.report_slack")
    def test_create_conversion_request(self, mock_report_slack):
        conversion_repo.session.query(TransactionDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(ConversionTransactionDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(ConversionDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(WalletPairDBModel).delete()
        conversion_repo.session.commit()
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
        bad_request_incorrect_signature = {'status': 'failed', 'data': None,
                                           'error': {'code': 'E0006', 'message': 'BAD_REQUEST',
                                                     'details': 'Incorrect signature provided'}}

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
            "token_pair_id": "33477fd4ea994689a04646cbbaafd133",
            "amount": "1333.05",
            "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
            "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
            "block_number": 12345678,
            "signature": "0xd4159d88ccc844ced5f0fa19b2975877813ab82f5c260d8cbacc1c11e9d61e8c776db78473a052ee02da961e98c7326f70c5e37e9caa2240dbb17baea2d4c69c1b"
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_token_pair_id_not_exists)

        body_input = json.dumps({
            "token_pair_id": "22477fd4ea994689a04646cbbaafd133",
            "amount": "1333.05",
            "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
            "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
            "block_number": 123456789,
            "signature": "0xd4159d88ccc844ced5f0fa19b2975877813ab82f5c260d8cbacc1c11e9d61e8c776db78473a052ee02da961e98c7326f70c5e37e9caa2240dbb17baea2d4c69c1b"
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_incorrect_signature)

        body_input = json.dumps({
            "token_pair_id": "32477fd4ea994689a04646cbbaafd133",
            "amount": "1333.05",
            "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
            "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
            "block_number": 12345678,
            "signature": "0xd4159d88ccc844ced5f0fa19b2975877813ab82f5c260d8cbacc1c11e9d61e8c776db78473a052ee02da961e98c7326f70c5e37e9caa2240dbb17baea2d4c69c1b"
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_token_pair_id_not_exists)

        # success request
        body_input = json.dumps({
            "token_pair_id": "22477fd4ea994689a04646cbbaafd133",
            "amount": "1333.05",
            "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
            "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
            "block_number": 12345678,
            "signature": "0xd4159d88ccc844ced5f0fa19b2975877813ab82f5c260d8cbacc1c11e9d61e8c776db78473a052ee02da961e98c7326f70c5e37e9caa2240dbb17baea2d4c69c1b"
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(len(body["data"]), 2)
        self.assertIsNotNone(body["data"]["id"])
        self.assertIsNone(body["data"]["deposit_address"])
        previous_request_id = body["data"]["id"]

        body_input = json.dumps({
            "token_pair_id": "22477fd4ea994689a04646cbbaafd133",
            "amount": "1333.05",
            "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
            "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
            "block_number": 12345678,
            "signature": "0xd4159d88ccc844ced5f0fa19b2975877813ab82f5c260d8cbacc1c11e9d61e8c776db78473a052ee02da961e98c7326f70c5e37e9caa2240dbb17baea2d4c69c1b"
        })
        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(len(body["data"]), 2)
        self.assertIsNotNone(body["data"]["id"])
        self.assertIsNone(body["data"]["deposit_address"])
        self.assertEqual(body["data"]["id"], previous_request_id)

        # Length of wallet pair table should be one because , the request is from same from and to address
        wallet_pair_count = conversion_repo.session.query(distinct(WalletPairDBModel.id)).all()
        self.assertEqual(len(wallet_pair_count), 1)

        body_input = json.dumps({
            "token_pair_id": "fdd6a416d8414154bcdd95f82b6ab239",
            "amount": "1333.05",
            "from_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
            "to_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
            "block_number": 12345678,
            "signature": "0x84cad9a7adbd444f156906a44381135ae2d81140fb4a0a0ea286287706c36eda643268252c6760f18309aa6f8396b53a48d1ffa9784f326b880758b8f11f03d21b"
        })

        event["body"] = body_input
        response = create_conversion_request(event, {})
        body = json.loads(response["body"])
        self.assertEqual(len(body["data"]), 2)
        self.assertIsNotNone(body["data"]["id"])
        self.assertIsNotNone(body["data"]["deposit_address"])
        self.assertNotEqual(body["data"]["id"], previous_request_id)

        # Length of wallet pair table should be two because , the request is from different from and to address
        wallet_pair_count = conversion_repo.session.query(distinct(WalletPairDBModel.id)).all()
        self.assertEqual(len(wallet_pair_count), 2)

    @patch("common.utils.Utils.report_slack")
    def test_get_conversion_history(self, mock_report_slack):
        bad_request_schema_not_matching = {'status': 'failed', 'data': None,
                                           'error': {'code': 'E0003', 'message': 'BAD_REQUEST',
                                                     'details': 'Schema is not matching with request'}}
        bad_request_property_value_empty = {'status': 'failed', 'data': None,
                                            'error': {'code': 'E0005', 'message': 'BAD_REQUEST',
                                                      'details': 'Property value is empty'}}
        success_response_with_history = {'status': 'success', 'data': {'items': [{'conversion': {
            'id': '7298bce110974411b260cac758b37ee0', 'deposit_amount': '1.33305E+8', 'claim_amount': None,
            'fee_amount': None, 'status': 'USER_INITIATED', 'updated_at': '2022-01-12 04:10:54'}, 'wallet_pair': {
            'from_address': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1',
            'to_address': 'addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8'},
                                                                                  'from_token': {
                                                                                      'name': 'Singularity Cardano',
                                                                                      'symbol': 'AGIX',
                                                                                      'blockchain': {'name': 'Cardano',
                                                                                                     'symbol': 'ADA',
                                                                                                     'chain_id': 2}},
                                                                                  'to_token': {
                                                                                      'name': 'Singularity Ethereum',
                                                                                      'symbol': 'AGIX',
                                                                                      'blockchain': {'name': 'Ethereum',
                                                                                                     'symbol': 'ETH',
                                                                                                     'chain_id': 42}},
                                                                                  'transaction': []}, {'conversion': {
            'id': '51769f201e46446fb61a9c197cb0706b', 'deposit_amount': '1.66305E+18', 'claim_amount': None,
            'fee_amount': None, 'status': 'PROCESSING', 'updated_at': '2022-01-12 04:10:54'}, 'wallet_pair': {
            'from_address': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1',
            'to_address': 'addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8'},
                                                                                                       'from_token': {
                                                                                                           'name': 'Singularity Cardano',
                                                                                                           'symbol': 'AGIX',
                                                                                                           'blockchain': {
                                                                                                               'name': 'Cardano',
                                                                                                               'symbol': 'ADA',
                                                                                                               'chain_id': 2}},
                                                                                                       'to_token': {
                                                                                                           'name': 'Singularity Ethereum',
                                                                                                           'symbol': 'AGIX',
                                                                                                           'blockchain': {
                                                                                                               'name': 'Ethereum',
                                                                                                               'symbol': 'ETH',
                                                                                                               'chain_id': 42}},
                                                                                                       'transaction': [{
                                                                                                                           'id': '391be6385abf4b608bdd20a44acd6abc',
                                                                                                                           'transaction_operation': 'TOKEN_RECEIVED',
                                                                                                                           'transaction_hash': '22477fd4ea994689a04646cbbaafd133',
                                                                                                                           'transaction_amount': '1.66305E+18',
                                                                                                                           'status': 'SUCCESS',
                                                                                                                           'updated_at': '2022-01-12 04:10:54'},
                                                                                                                       {
                                                                                                                           'id': '1df60a2369f34247a5dc3ed29a8eef67',
                                                                                                                           'transaction_operation': 'TOKEN_RECEIVED',
                                                                                                                           'transaction_hash': '22477fd4ea994689a04646cbbaafd133',
                                                                                                                           'transaction_amount': '1.66305E+18',
                                                                                                                           'status': 'WAITING_FOR_CONFIRMATION',
                                                                                                                           'updated_at': '2022-01-12 04:10:54'}]},
                                                                                 {'conversion': {
                                                                                     'id': '5086b5245cd046a68363d9ca8ed0027e',
                                                                                     'deposit_amount': '1.33305E+18',
                                                                                     'claim_amount': None,
                                                                                     'fee_amount': None,
                                                                                     'status': 'USER_INITIATED',
                                                                                     'updated_at': '2022-01-12 04:10:54'},
                                                                                  'wallet_pair': {
                                                                                      'from_address': 'addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8',
                                                                                      'to_address': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1'},
                                                                                  'from_token': {
                                                                                      'name': 'Singularity Ethereum',
                                                                                      'symbol': 'AGIX',
                                                                                      'blockchain': {'name': 'Ethereum',
                                                                                                     'symbol': 'ETH',
                                                                                                     'chain_id': 42}},
                                                                                  'to_token': {
                                                                                      'name': 'Singularity Cardano',
                                                                                      'symbol': 'AGIX',
                                                                                      'blockchain': {'name': 'Cardano',
                                                                                                     'symbol': 'ADA',
                                                                                                     'chain_id': 2}},
                                                                                  'transaction': []}],
                                                                       'meta': {'total_records': 3, 'page_count': 1,
                                                                                'page_number': 1, 'page_size': 15}},
                                         'error': {'code': None, 'message': None, 'details': None}}
        success_response_with_no_history ={'status': 'success', 'data': {'items': [], 'meta': {'total_records': 0, 'page_count': 0, 'page_number': 1, 'page_size': 15}}, 'error': {'code': None, 'message': None, 'details': None}}

        # Bad Request
        event = dict()
        response = get_conversion_history(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_schema_not_matching)

        event = {"queryStringParameters": {"address": 4477, "page_number": "random number"}}
        response = get_conversion_history(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_schema_not_matching)

        event = {"queryStringParameters": {"address": ""}}
        response = get_conversion_history(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_property_value_empty)

        # valid request
        event = {"queryStringParameters": {"address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1"}}
        response = get_conversion_history(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response_with_history)

        event = {"queryStringParameters": {"address": "different address"}}
        response = get_conversion_history(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response_with_no_history)

    def tearDown(self):
        conversion_repo.session.query(TransactionDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(ConversionTransactionDBModel).delete()
        conversion_repo.session.commit()
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
