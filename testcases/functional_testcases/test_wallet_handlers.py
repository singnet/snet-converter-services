import json
import unittest
from unittest.mock import patch

from application.handler.wallet_handlers import get_all_deposit_address, get_wallets_address_by_ethereum_address
from infrastructure.models import TransactionDBModel, ConversionTransactionDBModel, ConversionDBModel, \
    WalletPairDBModel, TokenPairDBModel, ConversionFeeDBModel, TokenDBModel, BlockChainDBModel
from infrastructure.repositories.wallet_pair_repository import WalletPairRepository
from testcases.functional_testcases.test_variables import TestVariables

wallet_repo = WalletPairRepository()


class TestWallet(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        TestWallet.delete_all_tables()

    def setUp(self):
        wallet_repo.session.add_all(TestVariables().blockchain)
        wallet_repo.session.commit()
        wallet_repo.session.add_all(TestVariables().token)
        wallet_repo.session.commit()
        wallet_repo.session.add_all(TestVariables().conversion_fee)
        wallet_repo.session.commit()
        wallet_repo.session.add_all(TestVariables().token_pair)
        wallet_repo.session.commit()
        wallet_repo.session.add_all(TestVariables().wallet_pair)
        wallet_repo.session.commit()

    @patch("common.utils.Utils.report_slack")
    def test_get_wallets_address_by_ethereum_address(self, mock_report_slack):
        event = dict()

        bad_request_missing_value = {'status': 'failed', 'data': None,
                                     'error': {'code': 'E0005', 'message': 'BAD_REQUEST',
                                               'details': 'Property value is empty'}}
        bad_request_invalid_ethereum_address = {'status': 'failed', 'data': None,
                                                'error': {'code': 'E0059', 'message': 'BAD_REQUEST',
                                                          'details': 'Invalid ethereum address provided'}}
        success_response1 = {'status': 'success', 'data': {
            'cardano_address': 'addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8'},
                             'error': {'code': None, 'message': None, 'details': None}}
        success_response2 = {'data': {'cardano_address': None},
                             'error': {'code': None, 'details': None, 'message': None},
                             'status': 'success'}
        response = get_wallets_address_by_ethereum_address(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_missing_value)

        response = get_wallets_address_by_ethereum_address({"queryStringParameters": {"ethereum_address": ""}}, {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_missing_value)

        response = get_wallets_address_by_ethereum_address({"queryStringParameters": {"ethereum_address": "random"}},
                                                           {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_invalid_ethereum_address)

        response = get_wallets_address_by_ethereum_address(
            {"queryStringParameters": {"ethereum_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1"}},
            {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response1)

        response = get_wallets_address_by_ethereum_address(
            {"queryStringParameters": {"ethereum_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa3"}},
            {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response2)

    @patch("common.utils.Utils.report_slack")
    def test_get_all_deposit_address(self, mock_report_slack):
        event = dict()
        success_response = {'status': 'success', 'data': {'addresses': [
            'addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8']},
                            'error': {'code': None, 'message': None, 'details': None}}
        success_response_no_addresses = {'status': 'success', 'data': {'addresses': []},
                                         'error': {'code': None, 'message': None, 'details': None}}

        response = get_all_deposit_address(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response)

        TestWallet.delete_all_tables()

        response = get_all_deposit_address(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response_no_addresses)

    def tearDown(self):
        TestWallet.delete_all_tables()

    @staticmethod
    def delete_all_tables():
        wallet_repo.session.query(TransactionDBModel).delete()
        wallet_repo.session.commit()
        wallet_repo.session.query(ConversionTransactionDBModel).delete()
        wallet_repo.session.commit()
        wallet_repo.session.query(ConversionDBModel).delete()
        wallet_repo.session.commit()
        wallet_repo.session.query(WalletPairDBModel).delete()
        wallet_repo.session.commit()
        wallet_repo.session.query(TokenPairDBModel).delete()
        wallet_repo.session.commit()
        wallet_repo.session.query(ConversionFeeDBModel).delete()
        wallet_repo.session.commit()
        wallet_repo.session.query(TokenDBModel).delete()
        wallet_repo.session.commit()
        wallet_repo.session.query(BlockChainDBModel).delete()
        wallet_repo.session.commit()
