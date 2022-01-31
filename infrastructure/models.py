from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey, UniqueConstraint, DECIMAL, BOOLEAN, BIGINT, \
    func, TEXT, TIMESTAMP, text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BlockChainDBModel(Base):
    __tablename__ = "blockchain"
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)
    name = Column("name", VARCHAR(50), nullable=False)
    description = Column("description", TEXT, nullable=False)
    symbol = Column("symbol", VARCHAR(30), nullable=False)
    logo = Column("logo", VARCHAR(250), nullable=False)
    chain_id = Column("chain_id", INTEGER, nullable=False)
    block_confirmation = Column("block_confirmation", INTEGER, nullable=False)
    is_extension_available = Column("is_extension_available", BOOLEAN, default=False)
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)
    __table_args__ = (UniqueConstraint(name, symbol), {})


class TokenDBModel(Base):
    __tablename__ = "token"
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)
    name = Column("name", VARCHAR(50), nullable=False)
    description = Column("description", TEXT, nullable=False)
    symbol = Column("symbol", VARCHAR(30), nullable=False)
    logo = Column("logo", VARCHAR(250))
    blockchain_id = Column("blockchain_id", BIGINT, ForeignKey(BlockChainDBModel.row_id), nullable=False)
    allowed_decimal = Column("allowed_decimal", INTEGER)
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)
    blockchain_detail = relationship(BlockChainDBModel, uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(name, symbol, blockchain_id), {})


class ConversionFeeDBModel(Base):
    __tablename__ = "conversion_fee"
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)
    percentage_from_source = Column("percentage_from_source", DECIMAL(10, 5), nullable=False)
    amount = Column("amount", DECIMAL(64, 0))
    token_id = Column("token_id", BIGINT, ForeignKey(TokenDBModel.row_id))
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)
    token = relationship(TokenDBModel, foreign_keys=[token_id])


class TokenPairDBModel(Base):
    __tablename__ = "token_pair"
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)
    from_token_id = Column("from_token_id", BIGINT, ForeignKey(TokenDBModel.row_id), nullable=False)
    to_token_id = Column("to_token_id", BIGINT, ForeignKey(TokenDBModel.row_id), nullable=False)
    conversion_fee_id = Column("conversion_fee_id", BIGINT, ForeignKey(ConversionFeeDBModel.row_id))
    is_enabled = Column("is_enabled", BOOLEAN, default=True)
    min_value = Column("min_value", DECIMAL(64, 0))
    max_value = Column("max_value", DECIMAL(64, 0))
    contract_address = Column("contract_address", VARCHAR(250), nullable=False)
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)
    conversion_fee = relationship(ConversionFeeDBModel, foreign_keys=[conversion_fee_id])
    from_token = relationship(TokenDBModel, foreign_keys=[from_token_id])
    to_token = relationship(TokenDBModel, foreign_keys=[to_token_id])
    __table_args__ = (UniqueConstraint(from_token_id, to_token_id), {})


class WalletPairDBModel(Base):
    __tablename__ = "wallet_pair"
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)
    token_pair_id = Column("token_pair_id", BIGINT, ForeignKey(TokenPairDBModel.row_id), nullable=False)
    from_address = Column("from_address", VARCHAR(250), nullable=False)
    to_address = Column("to_address", VARCHAR(250), nullable=False)
    deposit_address = Column("deposit_address", VARCHAR(250))
    signature = Column("signature", VARCHAR(250), nullable=False)
    signature_metadata = Column("signature_metadata", JSON, nullable=False)
    signature_expiry = Column("signature_expiry", TIMESTAMP)
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)
    token_pair = relationship(TokenPairDBModel, foreign_keys=[token_pair_id], uselist=False, lazy="select")
    __table_args__ = (UniqueConstraint(from_address, to_address), {})


class ConversionDBModel(Base):
    __tablename__ = "conversion"
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)
    wallet_pair_id = Column("wallet_pair_id", BIGINT, ForeignKey(WalletPairDBModel.row_id), nullable=False)
    deposit_amount = Column("deposit_amount", DECIMAL(64, 0), nullable=False)
    claim_amount = Column("claim_amount", DECIMAL(64, 0))
    fee_amount = Column("fee_amount", DECIMAL(64, 0))
    status = Column("status", VARCHAR(30), nullable=False)
    claim_signature = Column("claim_signature", VARCHAR(250))
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)
    wallet_pair = relationship(WalletPairDBModel, foreign_keys=[wallet_pair_id], uselist=False, lazy="select")


class ConversionTransactionDBModel(Base):
    __tablename__ = "conversion_transaction"
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)
    conversion_id = Column("conversion_id", BIGINT, ForeignKey(ConversionDBModel.row_id), nullable=False)
    status = Column("status", VARCHAR(30))
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)
    conversion = relationship(ConversionDBModel, uselist=False, lazy="select")


class TransactionDBModel(Base):
    __tablename__ = "transaction"
    row_id = Column("row_id", BIGINT, primary_key=True, autoincrement=True)
    id = Column("id", VARCHAR(50), unique=True, nullable=False)
    conversion_transaction_id = Column("conversion_transaction_id", BIGINT,
                                       ForeignKey(ConversionTransactionDBModel.row_id),
                                       nullable=False)
    from_token_id = Column("from_token_id", BIGINT, ForeignKey(TokenDBModel.row_id), nullable=False)
    to_token_id = Column("to_token_id", BIGINT, ForeignKey(TokenDBModel.row_id), nullable=False)
    transaction_visibility = Column("transaction_visibility", VARCHAR(30))
    transaction_operation = Column("transaction_operation", VARCHAR(30))
    transaction_hash = Column("transaction_hash", VARCHAR(250))
    transaction_amount = Column("transaction_amount", DECIMAL(50, 20))
    status = Column("status", VARCHAR(30))
    created_by = Column("created_by", VARCHAR(50), nullable=False)
    created_at = Column("created_at", TIMESTAMP,
                        server_default=func.current_timestamp(), nullable=False)
    updated_at = Column("updated_at", TIMESTAMP,
                        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                        nullable=False)
    conversion_transaction = relationship(ConversionTransactionDBModel, uselist=False, lazy="select")
    from_token = relationship(TokenDBModel, foreign_keys=[from_token_id])
    to_token = relationship(TokenDBModel, foreign_keys=[to_token_id])
