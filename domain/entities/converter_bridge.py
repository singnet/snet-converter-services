from decimal import Decimal

from constants.entity import ConverterBridgeEntities


class ConverterBridge:
    def __init__(self, blockchain_name: str, blockchain_network_id: int, conversion_id: str, tx_amount: Decimal,
                 tx_operation: str):
        self.blockchain_name = blockchain_name
        self.blockchain_network_id = blockchain_network_id
        self.conversion_id = conversion_id
        self.tx_amount = str(tx_amount.normalize())
        self.tx_operation = tx_operation

    def to_dict(self):
        return {
            ConverterBridgeEntities.BLOCKCHAIN_NAME.value: self.blockchain_name,
            ConverterBridgeEntities.BLOCKCHAIN_EVENT.value: {
                ConverterBridgeEntities.CONVERSION_ID.value: self.conversion_id,
                ConverterBridgeEntities.TX_AMOUNT.value: self.tx_amount,
                ConverterBridgeEntities.TX_OPERATION.value: self.tx_operation,
            },
            ConverterBridgeEntities.BLOCKCHAIN_NETWORK_ID.value: self.blockchain_network_id
        }
