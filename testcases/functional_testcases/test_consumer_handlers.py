import json
import unittest
from unittest.mock import patch

from application.handler.consumer_handlers import converter_event_consumer, converter_bridge
from infrastructure.models import TransactionDBModel, ConversionTransactionDBModel, ConversionDBModel, \
    WalletPairDBModel, TokenPairDBModel, ConversionFeeDBModel, TokenDBModel, BlockChainDBModel
from infrastructure.repositories.conversion_repository import ConversionRepository
from testcases.functional_testcases.test_variables import TestVariables, consumer_token_received_event_message, \
    prepare_consumer_cardano_event_format, prepare_converter_bridge_event_format

conversion_repo = ConversionRepository()


class TestConsumer(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        TestConsumer.delete_all_tables()

    def setUp(self):
        conversion_repo.session.add_all(TestVariables().blockchain)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(TestVariables().token)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(TestVariables().conversion_fee)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(TestVariables().token_pair)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(TestVariables().wallet_pair)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(TestVariables().conversion)
        conversion_repo.session.commit()

    @patch("utils.sqs.SqsService.send_message_to_queue")
    @patch("utils.cardano_blockchain.CardanoBlockchainUtil.get_block")
    @patch("utils.cardano_blockchain.CardanoBlockchainUtil.get_transaction")
    @patch("utils.blockchain.check_block_confirmation")
    @patch("application.service.notification_service.NotificationService.send_message_to_queue")
    @patch("utils.blockchain.validate_cardano_address")
    @patch("common.utils.Utils.report_slack")
    def test_converter_event_consumer(self, mock_report_slack, mock_validate_cardano_address,
                                      mock_send_message_to_queue, mock_check_block_confirmation, mock_get_transaction,
                                      mock_get_block, mock_send_message_to_sqs):
        bad_request_missing_inputs = {'status': 'failed', 'data': None,
                                      'error': {'code': 'E0019', 'message': 'BAD_REQUEST',
                                                'details': 'Missing required inputs '}}
        bad_request_unsupported_blockchain = {'status': 'failed', 'data': None,
                                              'error': {'code': 'E0020', 'message': 'BAD_REQUEST',
                                                        'details': 'Unsupported blockchain provided to the system'}}
        not_enough_block_confirmation = {'status': 'failed', 'data': None,
                                         'error': {'code': None, 'message': 'INTERNAL_SERVER_ERROR',
                                                   'details': 'BlockConfirmationNotEnoughException()'}}
        missing_cardano_required_fields = {'status': 'failed', 'data': None,
                                           'error': {'code': 'E0026', 'message': 'BAD_REQUEST',
                                                     'details': 'Missing cardano event required fields'}}

        wallet_pair_not_exists = {'status': 'failed', 'data': None, 'error': {'code': 'E0028', 'message': 'BAD_REQUEST',
                                                                              'details': 'Bad request received on the transaction'}}

        TestConsumer.delete_all_tables()
        response = converter_event_consumer(prepare_consumer_cardano_event_format({}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_missing_inputs)

        response = converter_event_consumer(prepare_consumer_cardano_event_format({"hack": "test"}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_unsupported_blockchain)

        self.setUp()

        response = converter_event_consumer(prepare_consumer_cardano_event_format({"hack": "test"}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_missing_inputs)

        mock_get_block.return_value = {"confirmations": 0}
        response = converter_event_consumer(prepare_consumer_cardano_event_format(
            {"tx_hash": "random hash", "transaction_detail": {"tx_type": "TOKEN_RECEIVED"}}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, not_enough_block_confirmation)

        mock_get_block.return_value = {"confirmations": 100}
        response = converter_event_consumer(prepare_consumer_cardano_event_format(
            {"tx_hash": "random hash", "transaction_detail": {"tx_type": "TOKEN_RECEIVED"}}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, missing_cardano_required_fields)

        response = converter_event_consumer(prepare_consumer_cardano_event_format(
            {"tx_hash": "random hash", "address": "random address",
             "transaction_detail": {"tx_type": "TOKEN_RECEIVED", "tx_amount": "10000"}}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, wallet_pair_not_exists)

        input_event = prepare_consumer_cardano_event_format(consumer_token_received_event_message)
        # Update the existing conversion request
        converter_event_consumer(input_event, {})
        mock_send_message_to_queue.assert_called_with(queue="CONVERTER_BRIDGE",
                                                      message=json.dumps({'blockchain_name': 'Cardano',
                                                                          'blockchain_event': {
                                                                              'conversion_id': '5086b5245cd046a68363d9ca8ed0027e',
                                                                              'tx_amount': '1E+8',
                                                                              'tx_operation': 'TOKEN_BURNT'},
                                                                          'blockchain_network_id': 2}))

        conversion_count = conversion_repo.session.query(ConversionDBModel).all()
        self.assertEqual(3, len(conversion_count))
        conversion_transaction_count = conversion_repo.session.query(ConversionTransactionDBModel).all()
        self.assertEqual(1, len(conversion_transaction_count))

        # reprocess the same request, no impact and no change in state
        converter_event_consumer(input_event, {})

        conversion_count = conversion_repo.session.query(ConversionDBModel).all()
        self.assertEqual(3, len(conversion_count))
        conversion_transaction_count = conversion_repo.session.query(ConversionTransactionDBModel).all()
        self.assertEqual(1, len(conversion_transaction_count))
        conversion = conversion_repo.session.query(ConversionDBModel).filter(
            ConversionDBModel.id == '5086b5245cd046a68363d9ca8ed0027e').first()
        self.assertEqual("PROCESSING", conversion.status)

    @patch("common.utils.Utils.report_slack")
    def test_converter_bridge(self, mock_report_slack):
        bad_request_missing_bridge_fields = {'status': 'failed', 'data': None,
                                             'error': {'code': 'E0030', 'message': 'BAD_REQUEST',
                                                       'details': 'Missing converter bridge fields'}}
        bad_request_invalid_conversion_id = {'status': 'failed', 'data': None,
                                             'error': {'code': 'E0008', 'message': 'BAD_REQUEST',
                                                       'details': 'Invalid conversion id provided'}}
        bad_request_transactions_not_available = {'status': 'failed', 'data': None,
                                                  'error': {'code': 'E0036', 'message': 'BAD_REQUEST',
                                                            'details': 'No transactions available for this conversion'}}
        internal_server_transaction_wrongly_created = {'status': 'failed', 'data': None,
                                                       'error': {'code': 'E0037', 'message': 'INTERNAL_SERVER_ERROR',
                                                                 'details': 'Transaction wrongly created'}}

        response = converter_bridge(prepare_converter_bridge_event_format({}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_missing_bridge_fields)

        response = converter_bridge(prepare_converter_bridge_event_format({'blockchain_name': 'Cardano',
                                                                           'blockchain_event': {
                                                                               'conversion_id': 'random id',
                                                                               'tx_amount': '1E+8',
                                                                               'tx_operation': 'TOKEN_BURNT'},
                                                                           'blockchain_network_id': 2}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_invalid_conversion_id)

        response = converter_bridge(prepare_converter_bridge_event_format({'blockchain_name': 'Cardano',
                                                                           'blockchain_event': {
                                                                               'conversion_id': '5086b5245cd046a68363d9ca8ed0027e',
                                                                               'tx_amount': '1E+8',
                                                                               'tx_operation': 'TOKEN_BURNT'},
                                                                           'blockchain_network_id': 2}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, bad_request_transactions_not_available)

        conversion_repo.session.add_all(TestVariables().conversion_transaction)
        conversion_repo.session.commit()
        conversion_repo.session.add_all(TestVariables().transaction)
        conversion_repo.session.commit()

        response = converter_bridge(prepare_converter_bridge_event_format({'blockchain_name': 'Cardano',
                                                                           'blockchain_event': {
                                                                               'conversion_id': '51769f201e46446fb61a9c197cb0706b',
                                                                               'tx_amount': '1E+8',
                                                                               'tx_operation': 'TOKEN_BURNT'},
                                                                           'blockchain_network_id': 2}), {})
        body = json.loads(response["body"])
        self.assertEqual(body, internal_server_transaction_wrongly_created)
        conversion_repo.session.query(TransactionDBModel).delete()
        conversion_repo.session.commit()
        conversion_repo.session.query(ConversionTransactionDBModel).delete()
        conversion_repo.session.commit()

    def tearDown(self):
        TestConsumer.delete_all_tables()

    @staticmethod
    def delete_all_tables():
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
