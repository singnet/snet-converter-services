NETWORK = {
    "db": {
        "DB_DRIVER": "mysql+pymysql",
        "DB_HOST": "localhost",
        "DB_USER": "unittest_root",
        "DB_PASSWORD": "unittest_pwd",
        "DB_NAME": "converter_unittest_db",
        "DB_PORT": 3306,
        "DB_LOGGING": True,
    },
}

SLACK_HOOK = {
    "hostname": "",
    "port": 443,
    "path": "",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
}

CONVERTER_REPORTING_SLACK_HOOK = {
    "hostname": "",
    "port": 443,
    "path": "",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
}

BLOCKCHAIN_DETAILS = {
    "ethereum": {
        "network": {
            "mainnet": {
                "url": "https://mainnet.infura.io/v3/",
                "secret": {}
            },
            "ropsten": {
                "url": "https://ropsten.infura.io/v3/",
                "secret": {}
            },
            "kovan": {
                "url": "https://kovan.infura.io/v3/",
                "secret": {}
            },
            "goerli": {
                "url": "https://goerli.infura.io/v3/",
                "secret": {}
            },
            "sepolia": {
                "url": "https://sepolia.infura.io/v3/",
                "secret": {}
            },
        }
    },
    "binance": {
        "network": {
            "mainnet": {
                "url": "https://bsc-dataseed1.binance.org:443"
            },
            "testnet": {
                "url": "https://data-seed-prebsc-1-s1.binance.org:8545"
            }
        }
    },
    "cardano": {
        "network": {
            "mainnet": {
                "url": "https://cardano-mainnet.blockfrost.io/api",
                "secret": {
                    "project_id": "project_id"
                }
            },
            "testnet": {
                "url": "https://cardano-testnet.blockfrost.io/api",
                "secret": {
                    "project_id": "project_id"
                }
            },
            "preprod": {
                "url": "https://cardano-preprod.blockfrost.io/api",
                "secret": {
                    "project_id": "project_id"
                }
            }
        }
    }
}

TOPIC_DETAILS = {
}

QUEUE_DETAILS = {
    "CONVERTER_BRIDGE": "",
    "CONVERTER_BRIDGE_1": "",
    "CONVERTER_BRIDGE_2": "",
    "CONVERTER_BRIDGE_3": "",
    "CONVERTER_BRIDGE_4": "",
    "EVENT_CONSUMER": ""
}

TOKEN_CONTRACT_PATH = {
}

MAX_RETRY = {"BLOCK_CONFIRMATION": 0, "TRANSACTION_HASH_PRESENCE": 0}
SLEEP_TIME = {"BLOCK_CONFIRMATION": 0, "TRANSACTION_HASH_PRESENCE": 0}

SIGNATURE_EXPIRY_BLOCKS = {
    "CARDANO": 0,
    "ETHEREUM": 0,
    "BINANCE": 0
}

MESSAGE_GROUP_ID = ""

# In Hours
EXPIRE_CONVERSION = {
    "CARDANO": 0,
    "ETHEREUM": 0,
    "BINANCE": 0
}
