# snet-converter-services

Backend APIs as Conveter Services


```
Converter Service│   
├── v1
│   │   ├── blockchain  ----> (1)
│   │   └── other-services
```

***
## LIST OF APIs

 1. [Get all blockchain](#1-get-all-blockchain)




### 1. Get all blockchain
  API Url: `{DOMAIN_URL}/{STAGE}/v1/blockchain` 

  Method: `GET`

  Request :
```json5
{
  
}
```

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
      "logo": "",
      "chain_id": [
        "2"
      ],
      "created_at": "2022-01-12 04:10:54"
    },
    {
      "id": "a38b4038c3a04810805fb26056dfabdd",
      "name": "Ethereum",
      "description": "Connect with your wallet",
      "symbol": "ETH",
      "logo": "",
      "chain_id": [
        "42",
        "3"
      ],
      "created_at": "2022-01-12 04:10:54"
    }
  ],
  "error": {
    "code": null,
    "message": null,
    "details": null
  }
}
```