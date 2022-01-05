from sqlalchemy import Column, VARCHAR, TIMESTAMP, INTEGER, ForeignKey, UniqueConstraint, DECIMAL, BOOLEAN, BIGINT, \
    func, text, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AuditClass(object):
    id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    created_at = Column("created_at", TIMESTAMP(),
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP(),
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)


class BlockChainDetailDBModel(Base, AuditClass):
    __tablename__ = "blockchain_detail"
    chain_id = Column("chain_id", VARCHAR(50), nullable=False)
    name = Column("name", VARCHAR(50), nullable=False)
    symbol = Column("symbol", VARCHAR(30), nullable=False)
    logo = Column("logo", VARCHAR(250), nullable=False)
    block_confirmation = Column("block_confirmation", INTEGER, nullable=False)
    __table_args__ = (UniqueConstraint(chain_id, name, symbol), {})


class TokenDetailDBModel(Base, AuditClass):
    __tablename__ = "token_detail"
    name = Column("name", VARCHAR(50), nullable=False)
    description = Column("description", TEXT, nullable=False)
    symbol = Column("symbol", VARCHAR(30), nullable=False)
    logo = Column("logo", VARCHAR(250))
    blockchain_id = Column("blockchain_id", BIGINT, ForeignKey(BlockChainDetailDBModel.id), nullable=False)
    allowed_decimal = Column("allowed_decimal", INTEGER)
    blockchain_detail = relationship(BlockChainDetailDBModel, uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(blockchain_id, symbol), {})


class ConversionFeeDBModel(Base, AuditClass):
    __tablename__ = "conversion_fee"
    percentage_from_source = Column("percentage_from_source", DECIMAL)
    amount = Column("amount", BIGINT)
    token_id = Column("token_id", BIGINT, ForeignKey(TokenDetailDBModel.id))
    token_detail = relationship(TokenDetailDBModel, foreign_keys=[token_id])
    __table_args__ = (UniqueConstraint(AuditClass.id), {})


class TokenPairDBModel(Base, AuditClass):
    __tablename__ = "token_pair"
    from_token_id = Column("from_token_id", BIGINT, ForeignKey(TokenDetailDBModel.id), nullable=False)
    to_token_id = Column("to_token_id", BIGINT, ForeignKey(TokenDetailDBModel.id), nullable=False)
    conversion_fee_id = Column("conversion_fee_id", BIGINT, ForeignKey(ConversionFeeDBModel.id))
    is_enabled = Column("is_enabled", BOOLEAN, default=True)
    min_value = Column("min_value", BIGINT)
    max_value = Column("max_value", BIGINT)
    form_tn = relationship("TokenDetailDBModel", foreign_keys=[from_token_id])
    to_tn = relationship("TokenDetailDBModel", foreign_keys=[to_token_id])
    contract_address = Column("contract_address", VARCHAR(250))
    receiving_address = Column("receiving_address", VARCHAR(250))
    conversion_fee = relationship(ConversionFeeDBModel, foreign_keys=[conversion_fee_id])
    __table_args__ = (UniqueConstraint(from_token_id, to_token_id), {})


class WalletPairDBModel(Base, AuditClass):
    __tablename__ = "wallet_pair"
    wallet_pair_guid = Column("wallet_pair_guid", VARCHAR(250), nullable=False)
    token_pair_id = Column("token_pair_id", BIGINT, ForeignKey(TokenPairDBModel.id), nullable=False)
    from_address = Column("from_address", VARCHAR(250), nullable=False)
    to_address = Column("to_address", VARCHAR(250))
    token_pair = relationship(TokenPairDBModel, uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(wallet_pair_guid), {})


class ConversionDBModel(Base, AuditClass):
    __tablename__ = "conversion"
    conversion_guid = Column("conversion_guid", VARCHAR(250), nullable=False)
    wallet_pair_id = Column("wallet_pair_id", BIGINT, ForeignKey(WalletPairDBModel.id), nullable=False)
    amount = Column("amount", BIGINT)
    status = Column("status", VARCHAR(30), nullable=False)
    wallet_pair = relationship(WalletPairDBModel, uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(conversion_guid), {})


class TransactionDBModel(Base, AuditClass):
    __tablename__ = "transaction"
    transaction_guid = Column("transaction_guid", VARCHAR(250), nullable=False)
    conversion_id = Column("conversion_id", BIGINT, ForeignKey(ConversionDBModel.id), nullable=False)
    status = Column("status", VARCHAR(30), nullable=False)
    from_transaction_hash = Column("from_transaction_hash", VARCHAR(250))
    from_status = Column("from_status", VARCHAR(30))
    from_updated_at = Column("from_updated_at", TIMESTAMP)
    to_transaction_hash = Column("to_transaction_hash", VARCHAR(250))
    to_status = Column("to_status", VARCHAR(30))
    to_updated_at = Column("to_updated_at", TIMESTAMP)
    conversion = relationship(ConversionDBModel, uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(transaction_guid), {})
