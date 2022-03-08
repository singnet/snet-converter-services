import json

from constants.status import TransactionVisibility, TransactionOperation, TransactionStatus, \
    ConversionTransactionStatus, ConversionStatus
from infrastructure.models import BlockChainDBModel, TokenDBModel, TokenPairDBModel, ConversionFeeDBModel, \
    ConversionTransactionDBModel, ConversionDBModel, WalletPairDBModel, TransactionDBModel

DAPP_AS_CREATED_BY = "DApp"


def create_blockchain_record(row_id, id, name, description, symbol, logo, chain_id, block_confirmation,
                             is_extension_available,
                             created_by, created_at, updated_at):
    return BlockChainDBModel(row_id=row_id, id=id, name=name, description=description, symbol=symbol,
                             logo=logo, chain_id=chain_id, block_confirmation=block_confirmation,
                             is_extension_available=is_extension_available, created_by=created_by,
                             created_at=created_at, updated_at=updated_at)


def create_token_record(row_id, id, name, description, symbol, logo, blockchain_id, allowed_decimal, token_address,
                        created_by, created_at, updated_at):
    return TokenDBModel(row_id=row_id, id=id, name=name, description=description, symbol=symbol,
                        logo=logo, blockchain_id=blockchain_id, allowed_decimal=allowed_decimal,
                        token_address=token_address, created_by=created_by, created_at=created_at,
                        updated_at=updated_at)


def create_token_pair_record(row_id, id, from_token_id, to_token_id, min_value, max_value, contract_address,
                             conversion_fee_id, is_enabled, created_by, created_at, updated_at):
    return TokenPairDBModel(row_id=row_id, id=id, from_token_id=from_token_id, to_token_id=to_token_id,
                            min_value=min_value, max_value=max_value, contract_address=contract_address,
                            conversion_fee_id=conversion_fee_id, is_enabled=is_enabled, created_by=created_by,
                            created_at=created_at, updated_at=updated_at)


def create_conversion_fee(row_id, id, percentage_from_source, created_by, created_at, updated_at):
    return ConversionFeeDBModel(row_id=row_id, id=id, percentage_from_source=percentage_from_source,
                                created_by=created_by, created_at=created_at, updated_at=updated_at)


def create_wallet_pair(row_id, id, token_pair_id, from_address, to_address, deposit_address, deposit_address_detail,
                       signature,
                       signature_metadata, signature_expiry, created_by, created_at, updated_at):
    return WalletPairDBModel(row_id=row_id, id=id, token_pair_id=token_pair_id, from_address=from_address,
                             to_address=to_address, deposit_address=deposit_address,
                             deposit_address_detail=deposit_address_detail, signature=signature,
                             signature_metadata=signature_metadata, signature_expiry=signature_expiry,
                             created_by=created_by, created_at=created_at, updated_at=updated_at)


def create_conversion(row_id, id, wallet_pair_id, deposit_amount, claim_amount, fee_amount, status, claim_signature,
                      created_by, created_at, updated_at):
    return ConversionDBModel(row_id=row_id, id=id, wallet_pair_id=wallet_pair_id, deposit_amount=deposit_amount,
                             claim_amount=claim_amount, fee_amount=fee_amount, status=status,
                             claim_signature=claim_signature, created_by=created_by, created_at=created_at,
                             updated_at=updated_at)


def create_conversion_transaction(row_id, id, conversion_id, status, created_by, created_at, updated_at):
    return ConversionTransactionDBModel(row_id=row_id, id=id, conversion_id=conversion_id, status=status,
                                        created_by=created_by, created_at=created_at, updated_at=updated_at)


def create_transaction(row_id, id, conversion_transaction_id, from_token_id, to_token_id, transaction_visibility,
                       transaction_operation, transaction_hash, transaction_amount, status, created_by, created_at,
                       updated_at):
    return TransactionDBModel(row_id=row_id, id=id, conversion_transaction_id=conversion_transaction_id,
                              from_token_id=from_token_id, to_token_id=to_token_id,
                              transaction_visibility=transaction_visibility,
                              transaction_operation=transaction_operation, transaction_hash=transaction_hash,
                              transaction_amount=transaction_amount, status=status, created_by=created_by,
                              created_at=created_at, updated_at=updated_at)


class TestVariables:
    def __init__(self):
        created_at = "2022-01-12 04:10:54"
        created_at1 = "2022-01-11 04:10:54"
        created_at2 = "2022-01-10 04:10:54"
        updated_at = "2022-01-12 04:10:54"

        self.blockchain_row_id_1 = 1
        self.blockchain_row_id_2 = 2

        self.token_row_id_1 = 1
        self.token_row_id_2 = 2

        self.token_pair_row_id_1 = 1
        self.token_pair_row_id_2 = 2

        self.conversion_fee_row_id_1 = 1
        self.conversion_fee_row_id_2 = 2

        self.wallet_pair_id_1 = 1
        self.wallet_pair_id_2 = 2

        self.conversion_id_1 = 1
        self.conversion_id_2 = 2
        self.conversion_id_3 = 3

        self.conversion_transaction_id_1 = 1
        self.conversion_transaction_id_2 = 2

        self.transaction_id_1 = 1
        self.transaction_id_2 = 2
        self.transaction_id_3 = 3
        self.transaction_id_4 = 4

        self.blockchain = [
            create_blockchain_record(row_id=self.blockchain_row_id_1, id="a38b4038c3a04810805fb26056dfabdd",
                                     name="Ethereum",
                                     description="Connect with your wallet",
                                     symbol="ETH", logo="www.ethereum.com/image.png", chain_id=42,
                                     block_confirmation=25,
                                     is_extension_available=True, created_by=DAPP_AS_CREATED_BY, created_at=created_at,
                                     updated_at=updated_at),
            create_blockchain_record(row_id=self.blockchain_row_id_2, id="5b21294fe71a4145a40f6ab918a50f96",
                                     name="Cardano",
                                     description="Add your wallet address",
                                     symbol="ADA", logo="www.cardano.com/image.png", chain_id=2,
                                     block_confirmation=23,
                                     is_extension_available=False, created_by=DAPP_AS_CREATED_BY, created_at=created_at,
                                     updated_at=updated_at)
        ]
        self.token_record_1 = create_token_record(row_id=self.token_row_id_1, id="53ceafdb42ad4f3d81eeb19c674437f9",
                                                  name="Singularity Ethereum",
                                                  description="We are crazy on blockchain",
                                                  symbol="AGIX", logo="www.findOurUrl.com/image.png",
                                                  blockchain_id=self.blockchain_row_id_1, allowed_decimal=5,
                                                  token_address="0xA1e841e8F770E5c9507E2f8cfd0aA6f73009715d",
                                                  created_by=DAPP_AS_CREATED_BY,
                                                  created_at=created_at, updated_at=updated_at)
        self.token_record_2 = create_token_record(row_id=self.token_row_id_2, id="aa5763de861e4a52ab24464790a5c017",
                                                  name="Singularity Cardano",
                                                  description="We are crazy on blockchain",
                                                  symbol="AGIX", logo="www.findOurUrl.com/image.png",
                                                  blockchain_id=self.blockchain_row_id_2, allowed_decimal=10,
                                                  token_address="ae8a0b54484418a3db56f4e9b472d51cbc860667489366ba6e150c8a",
                                                  created_by=DAPP_AS_CREATED_BY,
                                                  created_at=created_at, updated_at=updated_at)
        self.token = [self.token_record_1, self.token_record_2]

        self.token_pair_record_1 = create_token_pair_record(row_id=self.token_pair_row_id_1,
                                                            id="22477fd4ea994689a04646cbbaafd133",
                                                            from_token_id=self.token_row_id_1,
                                                            to_token_id=self.token_row_id_2,
                                                            min_value=10, max_value=100000000,
                                                            contract_address="0xacontractaddress",
                                                            conversion_fee_id=self.conversion_fee_row_id_1,
                                                            is_enabled=True,
                                                            created_by=DAPP_AS_CREATED_BY,
                                                            created_at=created_at, updated_at=updated_at)

        self.token_pair_record_2 = create_token_pair_record(row_id=self.token_pair_row_id_2,
                                                            id="fdd6a416d8414154bcdd95f82b6ab239",
                                                            from_token_id=self.token_row_id_2,
                                                            to_token_id=self.token_row_id_1,
                                                            min_value=100, max_value=1000000000,
                                                            contract_address="0xacontractaddress",
                                                            conversion_fee_id=None, is_enabled=True,
                                                            created_by=DAPP_AS_CREATED_BY,
                                                            created_at=created_at, updated_at=updated_at)

        self.token_pair = [self.token_pair_record_1, self.token_pair_record_2]

        self.conversion_fee_record_1 = create_conversion_fee(row_id=self.conversion_fee_row_id_1,
                                                             id="ccd10383bd434bd7b1690754f8b98df3",
                                                             percentage_from_source=1.5,
                                                             created_by=DAPP_AS_CREATED_BY, created_at=created_at,
                                                             updated_at=updated_at)

        self.conversion_fee_record_2 = create_conversion_fee(row_id=self.conversion_fee_row_id_2,
                                                             id="099b90e8f60540228e3ccb948a1a708f",
                                                             percentage_from_source=2.23,
                                                             created_by=DAPP_AS_CREATED_BY, created_at=created_at,
                                                             updated_at=updated_at)
        self.conversion_fee = [self.conversion_fee_record_1, self.conversion_fee_record_2]

        self.wallet_pair = [
            create_wallet_pair(row_id=self.wallet_pair_id_1, id="1b0c8e059600478ca9de05e5fbb559b1",
                               token_pair_id=self.token_pair_row_id_1,
                               from_address="0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
                               to_address="addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
                               deposit_address=None, deposit_address_detail=None,
                               signature="0xd4159d88ccc844ced5f0fa19b2975877813ab82f5c260d8cbacc1c11e9d61e8c776db78473a052ee02da961e98c7326f70c5e37e9caa2240dbb17baea2d4c69c1b",
                               signature_metadata={"amount": "1333.05",
                                                   "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
                                                   "block_number": 12345678,
                                                   "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
                                                   "token_pair_id": "22477fd4ea994689a04646cbbaafd133"},
                               signature_expiry=None,
                               created_by=DAPP_AS_CREATED_BY, created_at=created_at, updated_at=updated_at),
            create_wallet_pair(row_id=self.wallet_pair_id_2, id="f8cff5ec5fd04d41afc32443117d2284",
                               token_pair_id=self.token_pair_row_id_2,
                               from_address="addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
                               to_address="0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
                               deposit_address="addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
                               deposit_address_detail={"derived_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8", "index": 1, "role": 0},
                               signature="0x84cad9a7adbd444f156906a44381135ae2d81140fb4a0a0ea286287706c36eda643268252c6760f18309aa6f8396b53a48d1ffa9784f326b880758b8f11f03d21b",
                               signature_metadata={"amount": "1333.05",
                                                   "to_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
                                                   "block_number": 12345678,
                                                   "from_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
                                                   "token_pair_id": "fdd6a416d8414154bcdd95f82b6ab239"},
                               signature_expiry=None,
                               created_by=DAPP_AS_CREATED_BY, created_at=created_at, updated_at=updated_at)
        ]
        self.conversion = [create_conversion(row_id=self.conversion_id_1, id="7298bce110974411b260cac758b37ee0",
                                             wallet_pair_id=self.wallet_pair_id_1, deposit_amount=133305000,
                                             claim_amount=None, fee_amount=None,
                                             status=ConversionStatus.USER_INITIATED.value,
                                             claim_signature=None, created_by=DAPP_AS_CREATED_BY,
                                             created_at=created_at,
                                             updated_at=updated_at),
                           create_conversion(row_id=self.conversion_id_2, id="5086b5245cd046a68363d9ca8ed0027e",
                                             wallet_pair_id=self.wallet_pair_id_2,
                                             deposit_amount=1333050000000000000,
                                             claim_amount=None, fee_amount=None,
                                             status=ConversionStatus.USER_INITIATED.value,
                                             claim_signature=None, created_by=DAPP_AS_CREATED_BY,
                                             created_at=created_at1,
                                             updated_at=updated_at),
                           create_conversion(row_id=self.conversion_id_3, id="51769f201e46446fb61a9c197cb0706b",
                                             wallet_pair_id=self.wallet_pair_id_1,
                                             deposit_amount=1663050000000000000,
                                             claim_amount=None, fee_amount=None,
                                             status=ConversionStatus.PROCESSING.value,
                                             claim_signature=None, created_by=DAPP_AS_CREATED_BY,
                                             created_at=created_at2,
                                             updated_at=updated_at)
                           ]
        self.conversion_transaction = [
            create_conversion_transaction(row_id=self.conversion_transaction_id_1,
                                          id="a33d4c759f884cd58b471b302c192fc6", conversion_id=self.conversion_id_3,
                                          status=ConversionTransactionStatus.FAILED.value,
                                          created_by=DAPP_AS_CREATED_BY, created_at=created_at, updated_at=updated_at),
            create_conversion_transaction(row_id=self.conversion_transaction_id_2,
                                          id="a942ea29b2ee4400ad9597443ca24645", conversion_id=self.conversion_id_3,
                                          status=ConversionTransactionStatus.PROCESSING.value,
                                          created_by=DAPP_AS_CREATED_BY, created_at=created_at, updated_at=updated_at)
        ]

        self.transaction = [
            create_transaction(row_id=self.transaction_id_1, id="391be6385abf4b608bdd20a44acd6abc",
                               conversion_transaction_id=self.conversion_transaction_id_2,
                               from_token_id=self.token_row_id_1, to_token_id=self.token_row_id_1,
                               transaction_visibility=TransactionVisibility.EXTERNAL.value,
                               transaction_operation=TransactionOperation.TOKEN_RECEIVED.value,
                               transaction_hash="22477fd4ea994689a04646cbbaafd133",
                               transaction_amount=1663050000000000000, status=TransactionStatus.SUCCESS.value,
                               created_by=DAPP_AS_CREATED_BY,
                               created_at=created_at, updated_at=updated_at),
            create_transaction(row_id=self.transaction_id_3, id="1df60a2369f34247a5dc3ed29a8eef67",
                               conversion_transaction_id=self.conversion_transaction_id_2,
                               from_token_id=self.token_row_id_2, to_token_id=self.token_row_id_2,
                               transaction_visibility=TransactionVisibility.EXTERNAL.value,
                               transaction_operation=TransactionOperation.TOKEN_RECEIVED.value,
                               transaction_hash="22477fd4ea994689a04646cbbaafd133",
                               transaction_amount=1663050000000000000,
                               status=TransactionStatus.WAITING_FOR_CONFIRMATION.value,
                               created_by=DAPP_AS_CREATED_BY, created_at=created_at, updated_at=updated_at)
        ]


def prepare_consumer_cardano_event_format(message):
    records = []
    body = {"Message": json.dumps(message)}
    records.append({"body": json.dumps(body)})
    input_event = {"Records": records}
    return input_event


def prepare_consumer_ethereum_event_format(name, data):
    return {"name": name, "data": data}


def prepare_converter_bridge_event_format(message):
    records = [{"body": json.dumps(message)}]
    input_event = {"Records": records}
    return input_event


consumer_token_received_event_message = {'id': '3f998ad2acd5427da9dcee73c9043b2f',
                                         'tx_hash': '1667dce54e1729aec07ab11342f2464335d6542530102e64f7dc47847f669449',
                                         'event_type': 'TOKEN_TRANSFER',
                                         'address': 'addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8',
                                         'event_status': None, 'updated_at': '2022-02-20 10:39:19',
                                         'asset': {'id': 'bc3e8590103d4d5cb2701f2faa2d5927',
                                                   'asset': '34d1adbf3a7e95b253fd0999fb85e2d41d4121b36b834b83ac069ebb41474958',
                                                   'policy_id': '34d1adbf3a7e95b253fd0999fb85e2d41d4121b36b834b83ac069ebb',
                                                   'asset_name': '41474958',
                                                   'allowed_decimal': 8,
                                                   'updated_at': '2022-02-20 10:39:15'},
                                         'transaction_detail': {'id': '6f1b5f9f7e654433baf6941986ec7e7d',
                                                                'tx_type': 'TOKEN_RECEIVED',
                                                                'assurance_level': 'HIGH', 'confirmations': 71514,
                                                                'tx_amount': '1E+8',
                                                                'tx_fee': '172101', 'block_number': 3263733,
                                                                'block_time': 1643042281,
                                                                'tx_metadata': {},
                                                                'updated_at': '2022-02-20 10:40:14'}}
