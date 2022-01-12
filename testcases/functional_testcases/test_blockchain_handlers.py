import json
import unittest

from application.handler.blockchain_handlers import get_all_blockchain
from infrastructure.models import BlockChainDBModel
from infrastructure.repositories.blockchain_repository import BlockchainRepository
from testcases.functional_testcases.test_variables import TestVariablesBlockchain

blockchain_repo = BlockchainRepository()


class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.tearDown()
        blockchain_repo.session.add_all(TestVariablesBlockchain().blockchain)
        blockchain_repo.session.commit()

    def test_get_all_blockchain(self):
        success_response_1 = {'status': 'success', 'data': [
            {'id': '5b21294fe71a4145a40f6ab918a50f96', 'name': 'Cardano', 'description': 'Add your wallet address',
             'symbol': 'ADA', 'logo': 'www.cardano.com/image.png', 'is_extension_available': False, 'chain_id': ['2'],
             'created_at': '2022-01-12 04:10:54'},
            {'id': 'a38b4038c3a04810805fb26056dfabdd', 'name': 'Ethereum', 'description': 'Connect with your wallet',
             'symbol': 'ETH', 'logo': 'www.ethereum.com/image.png', 'is_extension_available': True,
             'chain_id': ['42', '3'], 'created_at': '2022-01-12 04:10:54'}],
                              'error': {'code': None, 'message': None, 'details': None}}
        success_response_2 = {'status': 'success', 'data': [],
                              'error': {'code': None, 'message': None, 'details': None}}

        event = dict()
        # when data is seeded
        response = get_all_blockchain(event, {})
        print(response["body"])
        body = json.loads(response["body"])
        self.assertEqual(body, success_response_1)

        self.tearDown()

        # when data is not seeded
        response = get_all_blockchain(event, {})
        body = json.loads(response["body"])
        self.assertEqual(body, success_response_2)

    def tearDown(self):
        blockchain_repo.session.query(BlockChainDBModel).delete()
        blockchain_repo.session.commit()
