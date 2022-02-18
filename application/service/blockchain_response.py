from constants.entity import BlockchainEntities


def get_blockchain_response(blockchain):
    return {
        BlockchainEntities.ID.value: blockchain[BlockchainEntities.ID.value],
        BlockchainEntities.NAME.value: blockchain[BlockchainEntities.NAME.value],
        BlockchainEntities.DESCRIPTION.value: blockchain[BlockchainEntities.DESCRIPTION.value],
        BlockchainEntities.SYMBOL.value: blockchain[BlockchainEntities.SYMBOL.value],
        BlockchainEntities.LOGO.value: blockchain[BlockchainEntities.LOGO.value],
        BlockchainEntities.IS_EXTENSION_AVAILABLE.value: blockchain[BlockchainEntities.IS_EXTENSION_AVAILABLE.value],
        BlockchainEntities.CHAIN_ID.value: blockchain[BlockchainEntities.CHAIN_ID.value],
        BlockchainEntities.BLOCK_CONFIRMATION.value: blockchain[BlockchainEntities.BLOCK_CONFIRMATION.value],
        BlockchainEntities.UPDATED_AT.value: blockchain[BlockchainEntities.UPDATED_AT.value]
    }


def get_all_blockchain_response(blockchains):
    return [get_blockchain_response(blockchain) for blockchain in blockchains]


def get_blockchain_for_token_response(blockchain):
    return {
        BlockchainEntities.ID.value: blockchain[BlockchainEntities.ID.value],
        BlockchainEntities.NAME.value: blockchain[BlockchainEntities.NAME.value],
        BlockchainEntities.SYMBOL.value: blockchain[BlockchainEntities.SYMBOL.value],
        BlockchainEntities.CHAIN_ID.value: blockchain[BlockchainEntities.CHAIN_ID.value]
    }
