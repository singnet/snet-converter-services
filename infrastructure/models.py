from sqlalchemy import Column, VARCHAR, TIMESTAMP, INTEGER, ForeignKey, UniqueConstraint, DECIMAL, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AuditClass(object):
    created_at = Column("created_at", TIMESTAMP, nullable=False)
    updated_at = Column("updated_at", TIMESTAMP, nullable=False)


class BlockChainDetailDBModel(Base, AuditClass):
    __tablename__ = "blockchain_detail"
    id = Column("id", INTEGER, autoincrement=True, primary_key=True)
    chain_id = Column("chain_id", VARCHAR(50), nullable=False)
    name = Column("name", VARCHAR(50), nullable=False)
    symbol = Column("symbol", VARCHAR(30), nullable=False)
    logo = Column("logo", VARCHAR(250), nullable=False)
    block_confirmation = Column("block_confirmation", INTEGER, nullable=False)
    __table_args__ = (UniqueConstraint(chain_id, name, symbol), {})


class TokenDetailDBModel(Base, AuditClass):
    __tablename__ = "token_detail"
    id = Column("id", INTEGER, autoincrement=True, primary_key=True)
    name = Column("name", VARCHAR(50), nullable=False)
    description = Column("description", VARCHAR(250), nullable=False)
    symbol = Column("symbol", VARCHAR(30), nullable=False)
    logo = Column("logo", VARCHAR(250))
    blockchain_id = Column("blockchain_id", INTEGER, ForeignKey(BlockChainDetailDBModel.id), nullable=False)
    allowed_decimal = Column("allowed_decimal", INTEGER)
    blockchain_detail = relationship('BlockChainDetailDBModel', uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(blockchain_id, symbol), {})


class ConversionFeeDBModel(Base, AuditClass):
    __tablename__ = "conversion_fee"
    id = Column("id", VARCHAR(250), primary_key=True)
    percentage_from_source = Column("percentage_from_source", DECIMAL)
    amount = Column("amount", DECIMAL)
    token_id = Column("token_id", INTEGER, ForeignKey(TokenDetailDBModel.id))
    token_detail = relationship("TokenDetailDBModel", foreign_keys=[token_id])
    __table_args__ = (UniqueConstraint(id), {})


class TokenPairDBModel(Base, AuditClass):
    __tablename__ = "token_pair"
    id = Column("id", INTEGER, autoincrement=True, primary_key=True)
    from_token_id = Column("from_token_id", INTEGER, ForeignKey(TokenDetailDBModel.id), nullable=False)
    to_token_id = Column("to_token_id", INTEGER, ForeignKey(TokenDetailDBModel.id), nullable=False)
    conversion_fee_id = Column("conversion_fee_id", VARCHAR(250), ForeignKey(ConversionFeeDBModel.id))
    is_enabled = Column("is_enabled", BOOLEAN, default=True)
    min_value = Column("min_value", DECIMAL)
    max_value = Column("max_value", DECIMAL)
    form_tn = relationship("TokenDetailDBModel", foreign_keys=[from_token_id])
    to_tn = relationship("TokenDetailDBModel", foreign_keys=[to_token_id])
    contract_address = Column("contract_address", VARCHAR(250))
    receiving_address = Column("receiving_address", VARCHAR(250))
    conversion_fee = relationship("ConversionFeeDBModel", foreign_keys=[conversion_fee_id])
    __table_args__ = (UniqueConstraint(from_token_id, to_token_id), {})


class WalletPayerDBModel(Base, AuditClass):
    __tablename__ = "wallet_payer"
    id = Column("id", VARCHAR(250), primary_key=True)
    token_pair_id = Column("token_pair_id", INTEGER, ForeignKey(TokenPairDBModel.id), nullable=False)
    from_address = Column("from_address", VARCHAR(250), nullable=False)
    to_address = Column("to_address", VARCHAR(250))
    token_pair = relationship('TokenPairDBModel', uselist=False, lazy="select")


class ConversionDBModel(Base, AuditClass):
    __tablename__ = "conversion"
    id = Column("id", VARCHAR(250), primary_key=True)
    wallet_payer_id = Column("wallet_payer_id", VARCHAR(250), ForeignKey(WalletPayerDBModel.id), nullable=False)
    amount = Column("amount", DECIMAL)
    status = Column("status", VARCHAR(30), nullable=False)
    wallet_address = relationship('WalletAddressDBModel', uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(id), {})


class TransactionDBModel(Base, AuditClass):
    __tablename__ = "transaction"
    id = Column("id", VARCHAR(250), primary_key=True)
    conversion_id = Column("conversion_id", VARCHAR(250), ForeignKey(ConversionDBModel.id), nullable=False)
    status = Column("status", VARCHAR(30), nullable=False)
    from_transaction_hash = Column("from_transaction_hash", VARCHAR(250))
    from_status = Column("from_status", VARCHAR(30))
    from_updated_at = Column("from_updated_at", TIMESTAMP)
    to_transaction_hash = Column("to_transaction_hash", VARCHAR(250))
    to_status = Column("to_status", VARCHAR(30))
    to_updated_at = Column("to_updated_at", TIMESTAMP)
    conversion = relationship('ConversionDBModel', uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(id), {})
