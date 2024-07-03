import unittest

from utils.blockchain import is_valid_ethereum_address, is_valid_cardano_address


class TestAddressValidation(unittest.TestCase):
    def test_ethereum_address_validation(self):
        valid_ethereum_address = "0x4e934Fc82mmn84aBe1C1b2556b9bF3055dBdd43c"
        result = is_valid_ethereum_address(valid_ethereum_address)
        self.assertEqual(True, result)

        invalid_ethereum_address_short = "0x4e934Fc82mmn84aBe1"
        result = is_valid_ethereum_address(invalid_ethereum_address_short)
        self.assertEqual(False, result)

        invalid_ethereum_address_start = "x04e934Fc82mmn84aBe1C1b2556b9bF3055dBdd43c"
        result = is_valid_ethereum_address(invalid_ethereum_address_start)
        self.assertEqual(False, result)

    def test_cardano_address_validation(self):
        valid_cardano_address = "addr1q8v2v2whcj7tjagumt4cxjcma4aj8f8ev453fcxp40l80wdpdetpt7debugf8kyvwndem3ehlh0twf4vmqjdfvqtseaq7ynqs0"
        result = is_valid_cardano_address(valid_cardano_address)
        self.assertEqual(True, result)

        invalid_cardano_address = "q8v2v2whcj7tjagumt4cxjcma4aj8f8ev453fcxp40l80wdpdetpt7debugf8kyvwndem3ehlh0twf4vmqjdfvqtseaq7ynqs0"
        result = is_valid_cardano_address(invalid_cardano_address)
        self.assertEqual(False, result)

