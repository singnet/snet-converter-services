import json
import unittest
from unittest.mock import patch

from sqlalchemy.orm import make_transient

from application.handler.token_handlers import get_all_token_pair
from infrastructure.models import BlockChainDBModel, TokenDBModel, TokenPairDBModel, ConversionFeeDBModel
from infrastructure.repositories.token_repository import TokenRepository
from testcases.functional_testcases.test_variables import TestVariables

token_repo = TokenRepository()
test_variables = TestVariables()


class TestToken(unittest.TestCase):

    def setUp(self):
        self.tearDown()
        token_repo.session.add_all(test_variables.blockchain)
        token_repo.session.commit()
        token_repo.session.add_all(test_variables.token)
        token_repo.session.commit()
        token_repo.session.add_all(test_variables.conversion_fee)
        token_repo.session.commit()
        token_repo.session.add_all(test_variables.token_pair)
        token_repo.session.commit()

    @patch("common.utils.Utils.report_slack")
    def test_get_all_token_pair(self, mock_report_slack):
        success_response_1 = {'status': 'success', 'data': [
            {'id': '22477fd4ea994689a04646cbbaafd133', 'min_value': '1E+1', 'max_value': '1E+8',
             'contract_address': '0xacontractaddress',
             'from_token': {'id': '53ceafdb42ad4f3d81eeb19c674437f9', 'symbol': 'AGIX',
                            'logo': 'www.findOurUrl.com/image.png', 'allowed_decimal': 5,
                            'updated_at': '2022-01-12 04:10:54',
                            'blockchain': {'id': 'a38b4038c3a04810805fb26056dfabdd', 'name': 'Ethereum',
                                           'symbol': 'ETH', 'chain_id': 42}},
             'to_token': {'id': 'aa5763de861e4a52ab24464790a5c017', 'symbol': 'AGIX',
                          'logo': 'www.findOurUrl.com/image.png', 'allowed_decimal': 10,
                          'updated_at': '2022-01-12 04:10:54',
                          'blockchain': {'id': '5b21294fe71a4145a40f6ab918a50f96', 'name': 'Cardano', 'symbol': 'ADA',
                                         'chain_id': 2}},
             'conversion_fee': {'id': 'ccd10383bd434bd7b1690754f8b98df3', 'percentage_from_source': '1.5',
                                'updated_at': '2022-01-12 04:10:54'}, 'updated_at': '2022-01-12 04:10:54'},
            {'id': 'fdd6a416d8414154bcdd95f82b6ab239', 'min_value': '1E+2', 'max_value': '1E+9',
             'contract_address': '0xacontractaddress',
             'from_token': {'id': 'aa5763de861e4a52ab24464790a5c017', 'symbol': 'AGIX',
                            'logo': 'www.findOurUrl.com/image.png', 'allowed_decimal': 10,
                            'updated_at': '2022-01-12 04:10:54',
                            'blockchain': {'id': '5b21294fe71a4145a40f6ab918a50f96', 'name': 'Cardano', 'symbol': 'ADA',
                                           'chain_id': 2}},
             'to_token': {'id': '53ceafdb42ad4f3d81eeb19c674437f9', 'symbol': 'AGIX',
                          'logo': 'www.findOurUrl.com/image.png', 'allowed_decimal': 5,
                          'updated_at': '2022-01-12 04:10:54',
                          'blockchain': {'id': 'a38b4038c3a04810805fb26056dfabdd', 'name': 'Ethereum', 'symbol': 'ETH',
                                         'chain_id': 42}}, 'conversion_fee': {}, 'updated_at': '2022-01-12 04:10:54'}],
                              'error': {'code': None, 'message': None, 'details': None}}
        success_response_2 = {'status': 'success', 'data': [],
                              'error': {'code': None, 'message': None, 'details': None}}
        success_response_3 = {'status': 'success', 'data': [
            {'id': '22477fd4ea994689a04646cbbaafd133', 'min_value': '1E+1', 'max_value': '1E+8',
             'contract_address': '0xacontractaddress',
             'from_token': {'id': '53ceafdb42ad4f3d81eeb19c674437f9', 'symbol': 'AGIX',
                            'logo': 'www.findOurUrl.com/image.png', 'allowed_decimal': 5,
                            'updated_at': '2022-01-12 04:10:54',
                            'blockchain': {'id': 'a38b4038c3a04810805fb26056dfabdd', 'name': 'Ethereum',
                                           'symbol': 'ETH', 'chain_id': 42}},
             'to_token': {'id': 'aa5763de861e4a52ab24464790a5c017', 'symbol': 'AGIX',
                          'logo': 'www.findOurUrl.com/image.png', 'allowed_decimal': 10,
                          'updated_at': '2022-01-12 04:10:54',
                          'blockchain': {'id': '5b21294fe71a4145a40f6ab918a50f96', 'name': 'Cardano', 'symbol': 'ADA',
                                         'chain_id': 2}},
             'conversion_fee': {'id': 'ccd10383bd434bd7b1690754f8b98df3', 'percentage_from_source': '1.5',
                                'updated_at': '2022-01-12 04:10:54'}, 'updated_at': '2022-01-12 04:10:54'}],
                              'error': {'code': None, 'message': None, 'details': None}}

        event = dict()
        # when data is seeded
        response = get_all_token_pair(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response_1)
        self.assertEqual(len(body["data"]), 2)

        token_repo.session.query(TokenPairDBModel).delete()
        token_repo.session.commit()

        response = get_all_token_pair(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response_2)
        self.assertEqual(len(body["data"]), 0)

        make_transient(test_variables.token_pair_record_1)
        token_repo.session.add(test_variables.token_pair_record_1)
        token_repo.session.commit()

        response = get_all_token_pair(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response_3)
        self.assertEqual(len(body["data"]), 1)

    def tearDown(self):
        token_repo.session.query(TokenPairDBModel).delete()
        token_repo.session.commit()
        token_repo.session.query(ConversionFeeDBModel).delete()
        token_repo.session.commit()
        token_repo.session.query(TokenDBModel).delete()
        token_repo.session.commit()
        token_repo.session.query(BlockChainDBModel).delete()
        token_repo.session.commit()
