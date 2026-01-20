from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class Block(Base):
    __tablename__ = "blocks"

    number: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hash: Mapped[str] = mapped_column(String(66), unique=True, nullable=False, index=True)
    parent_hash: Mapped[str] = mapped_column(String(66), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    miner: Mapped[str] = mapped_column(String(42), nullable=False)
    difficulty: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_difficulty: Mapped[int] = mapped_column(BigInteger, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    extra_data: Mapped[str] = mapped_column(Text, nullable=False)
    gas_limit: Mapped[int] = mapped_column(BigInteger, nullable=False)
    gas_used: Mapped[int] = mapped_column(BigInteger, nullable=False)
    base_fee_per_gas: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="block", cascade="all, delete-orphan")
    logs: Mapped[List["Log"]] = relationship(back_populates="block", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_blocks_parent_hash", "parent_hash"),
        Index("idx_blocks_number", "number"),
    )

class Transaction(Base):
    __tablename__ = "transactions"

    hash: Mapped[str] = mapped_column(String(66), primary_key=True)
    nonce: Mapped[int] = mapped_column(Integer, nullable=False)
    block_hash: Mapped[str] = mapped_column(String(66), nullable=False, index=True)
    block_number: Mapped[int] = mapped_column(BigInteger, ForeignKey("blocks.number"), nullable=False, index=True)
    transaction_index: Mapped[int] = mapped_column(Integer, nullable=False)
    from_address: Mapped[str] = mapped_column(String(42), nullable=False, index=True)
    to_address: Mapped[Optional[str]] = mapped_column(String(42), nullable=True, index=True)
    value: Mapped[int] = mapped_column(BigInteger, nullable=False)
    gas_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    gas: Mapped[int] = mapped_column(BigInteger, nullable=False)
    input: Mapped[str] = mapped_column(Text, nullable=False)

    block: Mapped["Block"] = relationship(back_populates="transactions")
    logs: Mapped[List["Log"]] = relationship(back_populates="transaction", cascade="all, delete-orphan")

class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    log_index: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_hash: Mapped[str] = mapped_column(String(66), ForeignKey("transactions.hash"), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(42), nullable=False, index=True)
    data: Mapped[str] = mapped_column(Text, nullable=False)
    topics: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    block_number: Mapped[int] = mapped_column(BigInteger, ForeignKey("blocks.number"), nullable=False, index=True)
    block_hash: Mapped[str] = mapped_column(String(66), nullable=False, index=True)

    block: Mapped["Block"] = relationship(back_populates="logs")
    transaction: Mapped["Transaction"] = relationship(back_populates="logs")

    __table_args__ = (
        Index("idx_logs_transaction_hash", "transaction_hash"),
        Index("idx_logs_block_number", "block_number"),
    )
