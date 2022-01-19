# snet-converter-services

Backend APIs as Conveter Services


```
Converter Service│   
├── v1
│   │   ├── blockchain 
│   │       ├── GET         ----> (1) 
│   │   ├── token
│   │         ├── pair 
│   │           ├── GET     ----> (2)
│   │   ├── conversion  
│   │       ├── POST        ----> (3)
│   │   └── other-services
```

***
## LIST OF APIs

 1. [Get all blockchain](#1-get-all-blockchain)
 2. [Get all token pair](#2-get-all-token-pair)
 3. [Create conversion request](#3-create-a-conversion-request)


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
            "chain_id": [
                "2"
            ],
            "updated_at": "2022-01-12 04: 10: 54"
        },
        {
            "id": "a38b4038c3a04810805fb26056dfabdd",
            "name": "Ethereum",
            "description": "Connect with your wallet",
            "symbol": "ETH",
            "logo": "www.ethereum.com/image.png",
            "is_extension_available": true,
            "chain_id": [
                "42",
                "3"
            ],
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
                    "chain_id": [
                        "42",
                        "3"
                    ]
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
                    "chain_id": [
                        "42",
                        "3"
                    ]
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
                    "chain_id": [
                        "42",
                        "3"
                    ]
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
                    "chain_id": [
                        "2"
                    ]
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
                    "chain_id": [
                        "42",
                        "3"
                    ]
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
                    "chain_id": [
                        "2"
                    ]
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
    "token_pair_id": "3e24b15670ca42c49f8674ab38dbaf69",
    "amount": "1333.05",
    "from_address": "0xb3D785784136E96290E74F4E06e2d0695882B0C7",
    "to_address": "addr_test1qza8485avt2xn3vy63plawqt0gk3ykpf98wusc4qrml2avu0pkm5rp3pkz6q4n3kf8znlf3y749lll8lfmg5x86kgt8qju7vx8",
    "block_number": 2744,
    "signature": "0xb141a8178bc5765dd6dd366d6a1101ae086d9acb9fe56f0e5bededc575620377475828d978298833aea6ced6bd776427233c81e8b723bfb90de45da3387e05231c"
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
