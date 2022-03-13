import json
import unittest
from unittest.mock import patch

from application.handler.consumer_handlers import converter_event_consumer, converter_bridge
from constants.status import ConversionTransactionStatus, TransactionVisibility, TransactionOperation, TransactionStatus
from infrastructure.models import TransactionDBModel, ConversionTransactionDBModel, ConversionDBModel, \
    WalletPairDBModel, TokenPairDBModel, ConversionFeeDBModel, TokenDBModel, BlockChainDBModel
from infrastructure.repositories.conversion_repository import ConversionRepository
from testcases.functional_testcases.test_variables import TestVariables, consumer_token_received_event_message, \
    prepare_consumer_cardano_event_format, prepare_converter_bridge_event_format, \
    prepare_consumer_ethereum_event_format, create_conversion_transaction, DAPP_AS_CREATED_BY, create_transaction
from utils.exceptions import InternalServerErrorException, BlockConfirmationNotEnoughException

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

    @patch("utils.blockchain.get_ethereum_transaction_details")
    @patch("utils.blockchain.validate_cardano_transaction_details_against_conversion")
    @patch("utils.sqs.SqsService.send_message_to_queue")
    @patch("utils.cardano_blockchain.CardanoBlockchainUtil.get_block")
    @patch("utils.cardano_blockchain.CardanoBlockchainUtil.get_transaction")
    @patch("application.service.notification_service.NotificationService.send_message_to_queue")
    @patch("utils.blockchain.validate_cardano_address")
    @patch("common.utils.Utils.report_slack")
    def test_converter_event_consumer(self, mock_report_slack, mock_validate_cardano_address,
                                      mock_send_message_to_queue, mock_get_transaction,
                                      mock_get_block, mock_send_message_to_sqs,
                                      mock_validate_cardano_transaction_details_against_conversion,
                                      mock_get_ethereum_transaction_details):
        TestConsumer.delete_all_tables()

        # Internal server error when passing empty consumer event
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_cardano_event_format({}), {})

        # Internal server error when no data is feeded in consumer side
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_cardano_event_format({"hack": "test"}), {})

        self.setUp()

        # Internal server error when expected fields is not there
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_cardano_event_format({"hack": "test"}), {})

        mock_get_block.return_value = {"confirmations": 0}
        # Internal Server error  when expected fields is not there
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_cardano_event_format(
                              {"tx_hash": "random hash", "transaction_detail": {"tx_type": "TOKEN_RECEIVED"}}), {})

        # No action when wallet pair doesn't exist
        response = converter_event_consumer(prepare_consumer_cardano_event_format(
            {"tx_hash": "random hash", "address": "random address",
             "transaction_detail": {"tx_type": "TOKEN_RECEIVED", "tx_amount": "10000"}}), {})
        self.assertEqual(response, None)

        # valid request
        # Blockchain confirmation not enough error  when block confirmation not meet
        self.assertRaises(BlockConfirmationNotEnoughException, converter_event_consumer,
                          prepare_consumer_cardano_event_format(
                              {"tx_hash": "1667dce54e1729aec07ab11342f2464335d6542530102e64f7dc47847f669449",
                               "address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
                               "transaction_detail": {"tx_type": "TOKEN_RECEIVED",
                                                      "tx_amount": "1E+8"}}), {})
        transaction = conversion_repo.session.query(TransactionDBModel).filter(
            TransactionDBModel.transaction_hash == "1667dce54e1729aec07ab11342f2464335d6542530102e64f7dc47847f669449").first()
        self.assertEqual(transaction.status, TransactionStatus.WAITING_FOR_CONFIRMATION.value)
        self.assertEqual(transaction.confirmation, 0)

        mock_get_block.return_value = {"confirmations": 20}
        # Blockchain confirmation not enough error  when block confirmation not meet
        self.assertRaises(BlockConfirmationNotEnoughException, converter_event_consumer,
                          prepare_consumer_cardano_event_format(
                              {"tx_hash": "1667dce54e1729aec07ab11342f2464335d6542530102e64f7dc47847f669449",
                               "address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
                               "transaction_detail": {"tx_type": "TOKEN_RECEIVED",
                                                      "tx_amount": "1E+8"}}), {})
        transaction = conversion_repo.session.query(TransactionDBModel).filter(
            TransactionDBModel.transaction_hash == "1667dce54e1729aec07ab11342f2464335d6542530102e64f7dc47847f669449").first()
        self.assertEqual(transaction.status, TransactionStatus.WAITING_FOR_CONFIRMATION.value)
        self.assertEqual(transaction.confirmation, 20)

        mock_get_block.return_value = {"confirmations": 26}
        input_event = prepare_consumer_cardano_event_format(consumer_token_received_event_message)
        converter_event_consumer(input_event, {})
        # expected message format to send
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

        TestConsumer.delete_all_tables()

        # Internal server error when passing empty consumer event
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_ethereum_event_format("name", "data"), {})

        # Internal server error when no data is feeded in consumer side
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_ethereum_event_format("name fake", {"event": "fake"}), {})

        self.setUp()

        # Internal server error when expected fields is not there
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_ethereum_event_format("name fake", {"event": "fake"}), {})

        # Internal Server error  when expected fields is not there
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_ethereum_event_format("name fake",
                                                                 {"name": "fake", "transactionHash": "some hash",
                                                                  "event": "ConversionOut",
                                                                  "json_str": ""}),
                          {})

        # Internal Server error  when missing contract event details
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_ethereum_event_format("ConversionOut",
                                                                 {"transactionHash": "some hash",
                                                                  "event": "ConversionOut",
                                                                  "json_str": "{'conversionId': b'd78aeaf865d94ec8a8792d2847ef7323'}"}),
                          {})
        # Internal Server error  when giving invalid conversion id
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_ethereum_event_format("ConversionOut",
                                                                 {"transactionHash": "some hash",
                                                                  "event": "ConversionOut",
                                                                  "json_str": "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'd78aeaf865d94ec8a8792d2847ef7323', 'amount': 12345600}"}),
                          {})

        # Internal Server error  when amount/token holder doesn't match
        self.assertRaises(InternalServerErrorException, converter_event_consumer,
                          prepare_consumer_ethereum_event_format("ConversionOut",
                                                                 {"transactionHash": "some hash",
                                                                  "event": "ConversionOut",
                                                                  "json_str": "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'7298bce110974411b260cac758b37ee0', 'amount': 12345600}"}),
                          {})

        # Invalid address for transaction
        mock_get_ethereum_transaction_details.return_value = {"from": "some address"}
        converter_event_consumer(prepare_consumer_ethereum_event_format("ConversionOut",
                                                                        {
                                                                            "transactionHash": "0x5a557f3d556601acb3d42b18e364e3389223bedaa645f92953c07277c880047c",
                                                                            "event": "ConversionOut",
                                                                            "json_str": "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'7298bce110974411b260cac758b37ee0', 'amount': 133305000}"}),
                                 {})
        conversion_count = conversion_repo.session.query(ConversionDBModel).all()
        self.assertEqual(3, len(conversion_count))
        conversion_transaction_count = conversion_repo.session.query(ConversionTransactionDBModel).all()
        self.assertEqual(0, len(conversion_transaction_count))

        # valid event
        mock_get_ethereum_transaction_details.return_value = {"from": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1"}
        converter_event_consumer(prepare_consumer_ethereum_event_format("ConversionOut",
                                                                        {
                                                                            "transactionHash": "0x5a557f3d556601acb3d42b18e364e3389223bedaa645f92953c07277c880047c",
                                                                            "event": "ConversionOut",
                                                                            "json_str": "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'7298bce110974411b260cac758b37ee0', 'amount': 133305000}"}),
                                 {})
        mock_send_message_to_queue.assert_called_with(queue="CONVERTER_BRIDGE",
                                                      message=json.dumps({'blockchain_name': 'Cardano',
                                                                          'blockchain_event': {
                                                                              'conversion_id': '7298bce110974411b260cac758b37ee0',
                                                                              'tx_amount': '131305425',
                                                                              'tx_operation': 'TOKEN_MINTED'},
                                                                          'blockchain_network_id': 2}))
        conversion_count = conversion_repo.session.query(ConversionDBModel).all()
        self.assertEqual(3, len(conversion_count))
        conversion_transaction_count = conversion_repo.session.query(ConversionTransactionDBModel).all()
        self.assertEqual(1, len(conversion_transaction_count))
        conversion = conversion_repo.session.query(ConversionDBModel).filter(
            ConversionDBModel.id == '7298bce110974411b260cac758b37ee0').first()
        self.assertEqual("PROCESSING", conversion.status)

        transaction = conversion_repo.session.query(TransactionDBModel).first()
        self.assertEqual(transaction.transaction_operation, "TOKEN_BURNT")

        # Reprocessing the same request
        response = converter_event_consumer(prepare_consumer_ethereum_event_format("ConversionOut",
                                                                                   {
                                                                                       "transactionHash": "0x5a557f3d556601acb3d42b18e364e3389223bedaa645f92953c07277c880047c",
                                                                                       "event": "ConversionOut",
                                                                                       "json_str": "{'tokenHolder': '0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1', 'conversionId': b'7298bce110974411b260cac758b37ee0', 'amount': 133305000}"}),
                                            {})
        self.assertEqual(response, None)

    @patch("application.service.cardano_service.CardanoService.mint_token")
    @patch("common.utils.Utils.report_slack")
    def test_converter_bridge(self, mock_report_slack, mock_mint_token):
        mock_mint_token.return_value = {"transaction_id": "some hash"}

        # Internal server error because of missing required fields
        self.assertRaises(InternalServerErrorException, converter_bridge,
                          prepare_converter_bridge_event_format({}), {})

        # Internal server error because of invalid conversion id
        self.assertRaises(InternalServerErrorException, converter_bridge,
                          prepare_converter_bridge_event_format({'blockchain_name': 'Cardano',
                                                                 'blockchain_event': {
                                                                     'conversion_id': 'random id',
                                                                     'tx_amount': '1E+8',
                                                                     'tx_operation': 'TOKEN_BURNT'},
                                                                 'blockchain_network_id': 2}), {})

        # Internal server error because this conversion id doesn't have transactions
        self.assertRaises(InternalServerErrorException, converter_bridge,
                          prepare_converter_bridge_event_format({'blockchain_name': 'Cardano',
                                                                 'blockchain_event': {
                                                                     'conversion_id': '7298bce110974411b260cac758b37ee0',
                                                                     'tx_amount': '1E+8',
                                                                     'tx_operation': 'TOKEN_BURNT'},
                                                                 'blockchain_network_id': 2}), {})

        conversion = conversion_repo.session.query(ConversionDBModel).filter(
            ConversionDBModel.id == "7298bce110974411b260cac758b37ee0").first()
        conversion_repo.session.add_all([create_conversion_transaction(row_id=1,
                                                                       id="a33d4c759f884cd58b471b302c192fc6",
                                                                       conversion_id=conversion.row_id,
                                                                       status=ConversionTransactionStatus.PROCESSING.value,
                                                                       created_by=DAPP_AS_CREATED_BY,
                                                                       created_at="2022-01-12 04:10:54",
                                                                       updated_at="2022-01-12 04:10:54")])
        conversion_repo.session.add_all(
            [create_transaction(row_id=1, id="391be6385abf4b608bdd20a44acd6abc",
                                conversion_transaction_id=1,
                                from_token_id=TestVariables().token_row_id_1,
                                to_token_id=TestVariables().token_row_id_1,
                                transaction_visibility=TransactionVisibility.EXTERNAL.value,
                                transaction_operation=TransactionOperation.TOKEN_BURNT.value,
                                transaction_hash="22477fd4ea994689a04646cbbaafd133",
                                transaction_amount=1663050000000000000, confirmation=0,
                                status=TransactionStatus.SUCCESS.value,
                                created_by=DAPP_AS_CREATED_BY,
                                created_at="2022-01-12 04:10:54",
                                updated_at="2022-01-12 04:10:54")])

        # Internal server error because input event won't match with generated event
        self.assertRaises(InternalServerErrorException, converter_bridge,
                          prepare_converter_bridge_event_format({'blockchain_name': 'Cardano',
                                                                 'blockchain_event': {
                                                                     'conversion_id': '7298bce110974411b260cac758b37ee0',
                                                                     'tx_amount': '1E+8',
                                                                     'tx_operation': 'TOKEN_BURNT'},
                                                                 'blockchain_network_id': 2}), {})

        # valid request
        converter_bridge(prepare_converter_bridge_event_format({'blockchain_name': 'Cardano',
                                                                'blockchain_event': {
                                                                    'conversion_id': '7298bce110974411b260cac758b37ee0',
                                                                    'tx_amount': '131305425',
                                                                    'tx_operation': 'TOKEN_MINTED'},
                                                                'blockchain_network_id': 2}), {})
        transactions = conversion_repo.session.query(TransactionDBModel).all()
        self.assertEqual(len(transactions), 2)
        self.assertNotEqual(transactions[1].status, "SUCCESS")

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
