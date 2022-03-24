# Changelog

All notable changes to this Analytics Project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Released]

## 2022-03-24 12:00:00 

### Fixed
- Signature expiry check on conversion request using block number
- Block confirmation logic has been optimized and add the call to converter bridge
- Optimized the token pair api db calls 

## 2022-03-16 12:00:00 

### Added
- Added contract address for both claim and conversion request api
- Added allowed_decimal for transaction_history and conversion api

## 2022-03-13 12:00:00 

### Added
- Added confirmation to the transaction table
- API will be sending the confirmation to each transaction
- Consumer logic changed to handle the block confirmation

### Fixed
- Disabled cardano transaction updation from DApp because of security concerns
- Fixed address check on ethereum transaction updation from DApp and Consumer
- Avoid inserting 0 deposit amount into the conversion


## 2022-03-04 12:00:00 

### Added
- Added api to get the previous connected cardano address based on ethereum address 
- Added api to get the conversion detail(stepper)

### Moved
- get deposit function has been moved from conversion service to wallet service
- Moved cardano api's to cardano service

## 2022-02-28 16:00:00 

### Added
- Adding the token address
- Adding amount to response of conversion request


## 2022-02-23 16:00:00 

### Added
- Adding the signature on ethereum side to involve the methods

## 2022-01-25 16:00:00 

### Added
- Created the transaction conversion api and testcase
- Created the transaction history api and testcase
- Added the swagger documentation


## 2022-01-17 12:00:00 

### Added
- Added the token api, testcase and swagger documentation

## 2022-01-12 16:00:00 

### Added
- Setup the base code structures and utils
- Added the blockchain api and testcase
- Added the swagger documentation


