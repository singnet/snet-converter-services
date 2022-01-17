from infrastructure.models import BlockChainDBModel, TokenDBModel, TokenPairDBModel, ConversionFeeDBModel

DAPP_AS_CREATED_BY = "DApp"


def create_blockchain_record(row_id, id, name, description, symbol, logo, chain_id, block_confirmation,
                             is_extension_available,
                             created_by, created_at, updated_at):
    return BlockChainDBModel(row_id=row_id, id=id, name=name, description=description, symbol=symbol,
                             logo=logo, chain_id=chain_id, block_confirmation=block_confirmation,
                             is_extension_available=is_extension_available, created_by=created_by,
                             created_at=created_at, updated_at=updated_at)


def create_token_record(row_id, id, name, description, symbol, logo, blockchain_id, allowed_decimal, created_by,
                        created_at, updated_at):
    return TokenDBModel(row_id=row_id, id=id, name=name, description=description, symbol=symbol,
                        logo=logo, blockchain_id=blockchain_id, allowed_decimal=allowed_decimal, created_by=created_by,
                        created_at=created_at, updated_at=updated_at)


def create_token_pair_record(row_id, id, from_token_id, to_token_id, min_value, max_value, contract_address,
                             conversion_fee_id, is_enabled, created_by, created_at, updated_at):
    return TokenPairDBModel(row_id=row_id, id=id, from_token_id=from_token_id, to_token_id=to_token_id,
                            min_value=min_value,
                            max_value=max_value, contract_address=contract_address, conversion_fee_id=conversion_fee_id,
                            is_enabled=is_enabled, created_by=created_by, created_at=created_at, updated_at=updated_at)


def create_conversion_fee(row_id, id, percentage_from_source, created_by, created_at, updated_at):
    return ConversionFeeDBModel(row_id=row_id, id=id, percentage_from_source=percentage_from_source,
                                created_by=created_by, created_at=created_at, updated_at=updated_at)


class TestVariables:
    def __init__(self):
        created_at = "2022-01-12 04:10:54"
        updated_at = "2022-01-12 04:10:54"

        self.blockchain_row_id_1 = 1
        self.blockchain_row_id_2 = 2

        self.token_row_id_1 = 1
        self.token_row_id_2 = 2
        self.token_row_id_3 = 3
        self.token_row_id_4 = 4

        self.token_pair_row_id_1 = 1
        self.token_pair_row_id_2 = 2
        self.token_pair_row_id_3 = 3
        self.token_pair_row_id_4 = 4

        self.conversion_fee_row_id_1 = 1
        self.conversion_fee_row_id_2 = 2

        self.blockchain = [
            create_blockchain_record(row_id=self.blockchain_row_id_1, id="a38b4038c3a04810805fb26056dfabdd",
                                     name="Ethereum",
                                     description="Connect with your wallet",
                                     symbol="ETH", logo="www.ethereum.com/image.png", chain_id="42,3",
                                     block_confirmation=25,
                                     is_extension_available=True, created_by=DAPP_AS_CREATED_BY, created_at=created_at,
                                     updated_at=updated_at),
            create_blockchain_record(row_id=self.blockchain_row_id_2, id="5b21294fe71a4145a40f6ab918a50f96",
                                     name="Cardano",
                                     description="Add your wallet address",
                                     symbol="ADA", logo="www.cardano.com/image.png", chain_id="2",
                                     block_confirmation=23,
                                     is_extension_available=False, created_by=DAPP_AS_CREATED_BY, created_at=created_at,
                                     updated_at=updated_at)
        ]
        self.token_record_1 = create_token_record(row_id=self.token_row_id_1, id="53ceafdb42ad4f3d81eeb19c674437f9",
                                                  name="BattleBig",
                                                  description="We are crazy on blockchain",
                                                  symbol="AGIX", logo="www.findOurUrl.com/image.png",
                                                  blockchain_id=self.blockchain_row_id_1, allowed_decimal=5,
                                                  created_by=DAPP_AS_CREATED_BY,
                                                  created_at=created_at, updated_at=updated_at)
        self.token_record_2 = create_token_record(row_id=self.token_row_id_2, id="aa5763de861e4a52ab24464790a5c017",
                                                  name="Warriors",
                                                  description="We are crazy on blockchain",
                                                  symbol="NTX", logo="www.findOurUrl.com/image.png",
                                                  blockchain_id=self.blockchain_row_id_1, allowed_decimal=10,
                                                  created_by=DAPP_AS_CREATED_BY,
                                                  created_at=created_at, updated_at=updated_at)
        self.token_record_3 = create_token_record(row_id=self.token_row_id_3, id="928aac782db44a3da84ecd403513322c",
                                                  name="DeadRide",
                                                  description="We are crazy on blockchain",
                                                  symbol="AGIX", logo="www.findOurUrl.com/image.png",
                                                  blockchain_id=self.blockchain_row_id_2, allowed_decimal=15,
                                                  created_by=DAPP_AS_CREATED_BY,
                                                  created_at=created_at, updated_at=updated_at)
        self.token_record_4 = create_token_record(row_id=self.token_row_id_4, id="8fe5c3291abc4b2696e38a42ede55369",
                                                  name="JokerPlane",
                                                  description="We are crazy on blockchain",
                                                  symbol="NTX", logo="www.findOurUrl.com/image.png",
                                                  blockchain_id=self.blockchain_row_id_2, allowed_decimal=20,
                                                  created_by=DAPP_AS_CREATED_BY,
                                                  created_at=created_at, updated_at=updated_at)
        self.token = [self.token_record_1, self.token_record_2, self.token_record_3, self.token_record_4]

        self.token_pair_record_1 = create_token_pair_record(row_id=self.token_pair_row_id_1,
                                                            id="22477fd4ea994689a04646cbbaafd133",
                                                            from_token_id=self.token_row_id_1,
                                                            to_token_id=self.token_row_id_2,
                                                            min_value=10, max_value=100000000,
                                                            contract_address="0xacontractaddress",
                                                            conversion_fee_id=self.conversion_fee_row_id_1, is_enabled=True,
                                                            created_by=DAPP_AS_CREATED_BY,
                                                            created_at=created_at, updated_at=updated_at)

        self.token_pair_record_2 = create_token_pair_record(row_id=self.token_pair_row_id_2,
                                                            id="fdd6a416d8414154bcdd95f82b6ab239",
                                                            from_token_id=self.token_row_id_1,
                                                            to_token_id=self.token_row_id_3,
                                                            min_value=100, max_value=1000000000,
                                                            contract_address="0xacontractaddress",
                                                            conversion_fee_id=None, is_enabled=True,
                                                            created_by=DAPP_AS_CREATED_BY,
                                                            created_at=created_at, updated_at=updated_at)

        self.token_pair_record_3 = create_token_pair_record(row_id=self.token_pair_row_id_3,
                                                            id="6149fdfbdb81415c916636937c8ebe8e",
                                                            from_token_id=self.token_row_id_2,
                                                            to_token_id=self.token_row_id_4,
                                                            min_value=0.001, max_value=100,
                                                            contract_address="0xacontractaddress",
                                                            conversion_fee_id=self.conversion_fee_row_id_2, is_enabled=True,
                                                            created_by=DAPP_AS_CREATED_BY,
                                                            created_at=created_at, updated_at=updated_at)

        self.token_pair_record_4 = create_token_pair_record(row_id=self.token_pair_row_id_4,
                                                            id="08d3fe1f11e346af9b7fd5c408ebc1c0",
                                                            from_token_id=self.token_row_id_2,
                                                            to_token_id=self.token_row_id_3,
                                                            min_value=100, max_value=100000000,
                                                            contract_address="0xacontractaddress",
                                                            conversion_fee_id=None, is_enabled=False,
                                                            created_by=DAPP_AS_CREATED_BY,
                                                            created_at=created_at, updated_at=updated_at)

        self.token_pair = [self.token_pair_record_1, self.token_pair_record_2, self.token_pair_record_3,
                           self.token_pair_record_4]

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
