# snet-converter-services
[![CircleCI](https://circleci.com/gh/singnet/snet-cli.svg?style=svg)](https://circleci.com/gh/singnet/snet-converter-services)
<br>Backend APIs as Conveter Services


```
Converter Service│   
├── v1
│   │   ├── blockchain 
│   │       ├── GET           ----> (1) 
│   │   ├── token
│   │         ├── pair 
│   │           ├── GET       ----> (2)
│   │   ├── conversion  
│   │       ├── POST          ----> (3)
│   │       ├── history        
│   │           ├── POST      ----> (5)
│   │   ├── transaction  
│   │       ├── POST          ----> (4)
│   │   └── other-services
```

***
## LIST OF APIs

 1. [Get all blockchain](#1-get-all-blockchain)
 2. [Get all token pair](#2-get-all-token-pair)
 3. [Create conversion request](#3-create-a-conversion-request)
 4. [Create a Transaction for Conversion](#4-create-a-transaction-for-conversion)
 5. [Get Conversion History](#5-get-conversion-history)


### 1. Get all blockchain
  API Url: `{DOMAIN_URL}/{STAGE}/v1/blockchain` 

  Method: `GET`

  Request : No headers or params needed

  Response: 

```json5
{
    "status": "success",
    "data": [
        {
            "id": "5b21294fe71a4145a40f6ab918a50f96",
            "name": "Cardano",
            "description": "Add your wallet address",
            "symbol": "ADA",
            "logo": "www.cardano.com/image.png",
            "is_extension_available": false,
            "chain_id": 2,
            "updated_at": "2022-01-12 04: 10: 54"
        },
        {
            "id": "a38b4038c3a04810805fb26056dfabdd",
            "name": "Ethereum",
            "description": "Connect with your wallet",
            "symbol": "ETH",
            "logo": "www.ethereum.com/image.png",
            "is_extension_available": true,
            "chain_id": 42,
            "updated_at": "2022-01-12 04: 10: 54"
        }
    ],
    "error": {
        "code": null,
        "message": null,
        "details": null
    }
}
```


### 2. Get all token pair
  API Url: `{DOMAIN_URL}/{STAGE}/v1/token/pair` 

  Method: `GET`

  Request : No headers or params needed

  Response: 

```json5
{
    "status": "success",
    "data": [
        {
            "id": "22477fd4ea994689a04646cbbaafd133",
            "min_value": "1E+1",
            "max_value": "1E+8",
            "contract_address": "0xacontractaddress",
            "from_token": {
                "id": "53ceafdb42ad4f3d81eeb19c674437f9",
                "symbol": "AGIX",
                "allowed_decimal": 5,
                "updated_at": "2022-01-12 04:10:54",
                "blockchain": {
                    "id": "a38b4038c3a04810805fb26056dfabdd",
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "chain_id": 42,
                }
            },
            "to_token": {
                "id": "aa5763de861e4a52ab24464790a5c017",
                "symbol": "NTX",
                "allowed_decimal": 10,
                "updated_at": "2022-01-12 04:10:54",
                "blockchain": {
                    "id": "a38b4038c3a04810805fb26056dfabdd",
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "chain_id": 42,
                }
            },
            "conversion_fee": {
                "id": "ccd10383bd434bd7b1690754f8b98df3",
                "percentage_from_source": "1.5",
                "updated_at": "2022-01-12 04:10:54"
            },
            "updated_at": "2022-01-12 04:10:54"
        },
        {
            "id": "fdd6a416d8414154bcdd95f82b6ab239",
            "min_value": "1E+2",
            "max_value": "1E+9",
            "contract_address": "0xacontractaddress",
            "from_token": {
                "id": "53ceafdb42ad4f3d81eeb19c674437f9",
                "symbol": "AGIX",
                "allowed_decimal": 5,
                "updated_at": "2022-01-12 04:10:54",
                "blockchain": {
                    "id": "a38b4038c3a04810805fb26056dfabdd",
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "chain_id": 42,
                }
            },
            "to_token": {
                "id": "928aac782db44a3da84ecd403513322c",
                "symbol": "AGIX",
                "allowed_decimal": 15,
                "updated_at": "2022-01-12 04:10:54",
                "blockchain": {
                    "id": "5b21294fe71a4145a40f6ab918a50f96",
                    "name": "Cardano",
                    "symbol": "ADA",
                    "chain_id": 2
                }
            },
            "conversion_fee": {},
            "updated_at": "2022-01-12 04:10:54"
        },
        {
            "id": "6149fdfbdb81415c916636937c8ebe8e",
            "min_value": "0.001",
            "max_value": "1E+2",
            "contract_address": "0xacontractaddress",
            "from_token": {
                "id": "aa5763de861e4a52ab24464790a5c017",
                "symbol": "NTX",
                "allowed_decimal": 10,
                "updated_at": "2022-01-12 04:10:54",
                "blockchain": {
                    "id": "a38b4038c3a04810805fb26056dfabdd",
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "chain_id": 42
                }
            },
            "to_token": {
                "id": "8fe5c3291abc4b2696e38a42ede55369",
                "symbol": "NTX",
                "allowed_decimal": 20,
                "updated_at": "2022-01-12 04:10:54",
                "blockchain": {
                    "id": "5b21294fe71a4145a40f6ab918a50f96",
                    "name": "Cardano",
                    "symbol": "ADA",
                    "chain_id": 2
                }
            },
            "conversion_fee": {
                "id": "099b90e8f60540228e3ccb948a1a708f",
                "percentage_from_source": "2.23",
                "updated_at": "2022-01-12 04:10:54"
            },
            "updated_at": "2022-01-12 04:10:54"
        }
    ],
    "error": {
        "code": null,
        "message": null,
        "details": null
    }
}
```

### 3. Create a conversion request
  API Url: `{DOMAIN_URL}/{STAGE}/v1/conversion` 

  Method: `POST`

  Request :

```json5
{
  "token_pair_id": "22477fd4ea994689a04646cbbaafd133",
  "amount": "1333.05",
  "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
  "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
  "block_number": 12345678,
  "signature": "0xd4159d88ccc844ced5f0fa19b2975877813ab82f5c260d8cbacc1c11e9d61e8c776db78473a052ee02da961e98c7326f70c5e37e9caa2240dbb17baea2d4c69c1b"
}
```

  Response: 
```json5
{
  "status": "success",
  "data": {
    "id": "02bdcb4e65d1491586110cbf4a16efe8",
    "deposit_address": null
  },
  "error": {
    "code": null,
    "message": null,
    "details": null
  }
}
```

### 4. Create a Transaction for Conversion
  API Url: `{DOMAIN_URL}/{STAGE}/v1/transaction` 

  Method: `POST`

  Request :

```json5
{
  "conversion_id": "07e17d5165a74a79a8d4caa4a640caba",
  "transaction_hash": "22477fd4ea994689a04646cbbaafd133"
}
```

  Response: 
```json5
{
  "status": "success",
  "data": {
    "id": "e5c2a10ebe4e4a588ddb68c31a784ffa"
  },
  "error": {
    "code": null,
    "message": null,
    "details": null
  }
}
```

### 5. Get Conversion History
  API Url: `{DOMAIN_URL}/{STAGE}/v1/conversion/history` 

  Method: `GET`

  Request :

```json5
{
  "queryStringParameters":{
    "address" : "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
    "page_size":15,
    "page_number": 1
  }
}
```

  Response: 
```json5
{
    "status": "success",
    "data": {
        "items": [
            {
                "conversion": {
                    "id": "7298bce110974411b260cac758b37ee0",
                    "deposit_amount": "1.33305E+8",
                    "claim_amount": null,
                    "fee_amount": null,
                    "status": "USER_INITIATED",
                    "updated_at": "2022-01-12 04:10:54"
                },
                "wallet_pair": {
                    "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
                    "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8"
                },
                "from_token": {
                    "name": "Singularity Ethereum",
                    "symbol": "AGIX",
                    "blockchain": {
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "chain_id": 42
                    }
                },
                "to_token": {
                    "name": "Singularity Cardano",
                    "symbol": "AGIX",
                    "blockchain": {
                        "name": "Cardano",
                        "symbol": "ADA",
                        "chain_id": 2
                    }
                },
                "transactions": []
            },
            {
                "conversion": {
                    "id": "5086b5245cd046a68363d9ca8ed0027e",
                    "deposit_amount": "1.33305E+18",
                    "claim_amount": null,
                    "fee_amount": null,
                    "status": "USER_INITIATED",
                    "updated_at": "2022-01-12 04:10:54"
                },
                "wallet_pair": {
                    "from_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
                    "to_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1"
                },
                "from_token": {
                    "name": "Singularity Cardano",
                    "symbol": "AGIX",
                    "blockchain": {
                        "name": "Cardano",
                        "symbol": "ADA",
                        "chain_id": 2
                    }
                },
                "to_token": {
                    "name": "Singularity Ethereum",
                    "symbol": "AGIX",
                    "blockchain": {
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "chain_id": 42
                    }
                },
                "transactions": []
            },
            {
                "conversion": {
                    "id": "51769f201e46446fb61a9c197cb0706b",
                    "deposit_amount": "1.66305E+18",
                    "claim_amount": null,
                    "fee_amount": null,
                    "status": "PROCESSING",
                    "updated_at": "2022-01-12 04:10:54"
                },
                "wallet_pair": {
                    "from_address": "0xa18b95A9371Ac18C233fB024cdAC5ef6300efDa1",
                    "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8"
                },
                "from_token": {
                    "name": "Singularity Ethereum",
                    "symbol": "AGIX",
                    "blockchain": {
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "chain_id": 42
                    }
                },
                "to_token": {
                    "name": "Singularity Cardano",
                    "symbol": "AGIX",
                    "blockchain": {
                        "name": "Cardano",
                        "symbol": "ADA",
                        "chain_id": 2
                    }
                },
                "transactions": [
                    {
                        "id": "391be6385abf4b608bdd20a44acd6abc",
                        "transaction_operation": "TOKEN_RECEIVED",
                        "transaction_hash": "22477fd4ea994689a04646cbbaafd133",
                        "transaction_amount": "1.66305E+18",
                        "status": "SUCCESS",
                        "updated_at": "2022-01-12 04:10:54"
                    },
                    {
                        "id": "1df60a2369f34247a5dc3ed29a8eef67",
                        "transaction_operation": "TOKEN_RECEIVED",
                        "transaction_hash": "22477fd4ea994689a04646cbbaafd133",
                        "transaction_amount": "1.66305E+18",
                        "status": "WAITING_FOR_CONFIRMATION",
                        "updated_at": "2022-01-12 04:10:54"
                    }
                ]
            }
        ],
        "meta": {
            "total_records": 3,
            "page_count": 1,
            "page_number": 1,
            "page_size": 15
        }
    },
    "error": {
        "code": null,
        "message": null,
        "details": null
    }
}
```