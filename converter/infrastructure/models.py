from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey, UniqueConstraint, DECIMAL, BOOLEAN, BIGINT, \
    func, TEXT, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PrimaryKeyClass(object):
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)


class AuditClass(object):
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)


class BlockChainDBModel(Base, PrimaryKeyClass, AuditClass):
    __tablename__ = "blockchain"
    name = Column("name", VARCHAR(50), nullable=False)
    description = Column("description", TEXT, nullable=False)
    symbol = Column("symbol", VARCHAR(30), nullable=False)
    logo = Column("logo", VARCHAR(250), nullable=False)
    chain_id = Column("chain_id", VARCHAR(50), nullable=False)
    block_confirmation = Column("block_confirmation", INTEGER, nullable=False)
    is_extension_available = Column("is_enabled", BOOLEAN, default=True)
    __table_args__ = (UniqueConstraint(chain_id, name, symbol), {})


class TokenDBModel(Base, PrimaryKeyClass, AuditClass):
    __tablename__ = "token"
    name = Column("name", VARCHAR(50), nullable=False)
    description = Column("description", TEXT, nullable=False)
    symbol = Column("symbol", VARCHAR(30), nullable=False)
    logo = Column("logo", VARCHAR(250))
    blockchain_id = Column("blockchain_id", BIGINT, ForeignKey(BlockChainDBModel.row_id), nullable=False)
    allowed_decimal = Column("allowed_decimal", INTEGER)
    blockchain_detail = relationship(BlockChainDBModel, uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(blockchain_id, symbol), {})


class ConversionFeeDBModel(Base, PrimaryKeyClass, AuditClass):
    __tablename__ = "conversion_fee"
    percentage_from_source = Column("percentage_from_source", DECIMAL)
    amount = Column("amount", DECIMAL)
    token_id = Column("token_id", BIGINT, ForeignKey(TokenDBModel.row_id))
    token = relationship(TokenDBModel, foreign_keys=[token_id])


class TokenPairDBModel(Base, PrimaryKeyClass, AuditClass):
    __tablename__ = "token_pair"
    from_token_id = Column("from_token_id", BIGINT, ForeignKey(TokenDBModel.row_id), nullable=False)
    to_token_id = Column("to_token_id", BIGINT, ForeignKey(TokenDBModel.row_id), nullable=False)
    conversion_fee_id = Column("conversion_fee_id", BIGINT, ForeignKey(ConversionFeeDBModel.row_id))
    is_enabled = Column("is_enabled", BOOLEAN, default=True)
    min_value = Column("min_value", DECIMAL)
    max_value = Column("max_value", DECIMAL)
    contract_address = Column("contract_address", VARCHAR(250), nullable=False)
    conversion_fee = relationship(ConversionFeeDBModel, foreign_keys=[conversion_fee_id])
    form_token = relationship(TokenDBModel, foreign_keys=[from_token_id])
    to_token = relationship(TokenDBModel, foreign_keys=[to_token_id])
    __table_args__ = (UniqueConstraint(from_token_id, to_token_id), {})


class WalletPairDBModel(Base, PrimaryKeyClass, AuditClass):
    __tablename__ = "wallet_pair"
    token_pair_id = Column("token_pair_id", BIGINT, ForeignKey(TokenPairDBModel.row_id), nullable=False)
    from_address = Column("from_address", VARCHAR(250), nullable=False)
    to_address = Column("to_address", VARCHAR(250), nullable=False)
    deposit_address = Column("deposit_address", VARCHAR(250), unique=True)
    signature = Column("signature", VARCHAR(250))
    signature_expiry = Column("signature_expiry", TIMESTAMP, nullable=False)
    token_pair = relationship(TokenPairDBModel, foreign_keys=[token_pair_id], uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(from_address, to_address), {})


class ConversionDBModel(Base, PrimaryKeyClass, AuditClass):
    __tablename__ = "conversion"
    wallet_pair_id = Column("wallet_pair_id", BIGINT, ForeignKey(WalletPairDBModel.row_id), nullable=False)
    deposit_amount = Column("deposit_amount", DECIMAL, nullable=False)
    claim_amount = Column("claim_amount", DECIMAL)
    fee_amount = Column("fee_amount", DECIMAL)
    status = Column("status", VARCHAR(30), nullable=False)
    claim_signature = Column("claim_signature", VARCHAR(250))
    wallet_pair = relationship(WalletPairDBModel, foreign_keys=[wallet_pair_id], uselist=False, lazy="select")


class ConversionTransactionDBModel(Base, PrimaryKeyClass, AuditClass):
    __tablename__ = "conversion_transaction"
    conversion_id = Column("conversion_id", BIGINT, ForeignKey(ConversionDBModel.row_id), nullable=False)
    status = Column("status", VARCHAR(30))
    conversion = relationship(ConversionDBModel, uselist=False, lazy="select")


class TransactionDBModel(Base, PrimaryKeyClass, AuditClass):
    __tablename__ = "transaction"
    conversion_transaction_id = Column("conversion_transaction_id", BIGINT,
                                       ForeignKey(ConversionTransactionDBModel.row_id),
                                       nullable=False)
    from_token_id = Column("from_token_id", BIGINT, ForeignKey(TokenDBModel.row_id), nullable=False)
    to_token_id = Column("to_token_id", BIGINT, ForeignKey(TokenDBModel.row_id), nullable=False)
    transaction_visibility = Column("transaction_visibility", VARCHAR(30))
    transaction_operation = Column("transaction_operation", VARCHAR(30))
    transaction_hash = Column("transaction_hash", VARCHAR(250))
    transaction_amount = Column("transaction_amount", DECIMAL)
    status = Column("status", VARCHAR(30))
    conversion_transaction = relationship(ConversionTransactionDBModel, uselist=False, lazy="select")
    form_token = relationship(TokenDBModel, foreign_keys=[from_token_id])
    to_token = relationship(TokenDBModel, foreign_keys=[to_token_id])
