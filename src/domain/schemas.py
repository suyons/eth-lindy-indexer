import re
from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Hex string patterns
HEX_64_PATTERN = re.compile(r"^0x[a-fA-F0-9]{64}$")
HEX_40_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
HEX_ANY_PATTERN = re.compile(r"^0x[a-fA-F0-9]*$")

def validate_hex(v: str, length: Optional[int] = None) -> str:
    if not isinstance(v, str) or not v.startswith("0x"):
        raise ValueError("Hex string must start with 0x")
    if length and len(v) != length + 2:
        raise ValueError(f"Hex string must be {length} characters long (excluding 0x)")
    if not HEX_ANY_PATTERN.match(v):
        raise ValueError("Invalid hex characters")
    return v.lower()

# Custom Types for type hinting and basic pattern validation
Hash32 = Annotated[str, Field(pattern=r"^0x[a-fA-F0-9]{64}$")]
Address = Annotated[str, Field(pattern=r"^0x[a-fA-F0-9]{40}$")]
HexData = Annotated[str, Field(pattern=r"^0x[a-fA-F0-9]*$")]

class LogModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_index: int = Field(ge=0)
    transaction_hash: Hash32
    address: Address
    data: HexData
    topics: List[Hash32]
    block_number: int = Field(ge=0)
    block_hash: Hash32

    @field_validator("transaction_hash", "block_hash", mode="before")
    @classmethod
    def validate_hashes(cls, v: str) -> str:
        return validate_hex(v, 64)

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, v: str) -> str:
        return validate_hex(v, 40)

    @field_validator("topics", mode="before")
    @classmethod
    def validate_topics(cls, v: List[str]) -> List[str]:
        return [validate_hex(t, 64) for t in v]

class TransferEvent(BaseModel):
    from_address: Address
    to_address: Address
    value: int = Field(ge=0)
    transaction_hash: Hash32
    block_number: int = Field(ge=0)
    log_index: int = Field(ge=0)

    @field_validator("from_address", "to_address", mode="before")
    @classmethod
    def validate_addresses(cls, v: str) -> str:
        return validate_hex(v, 40)

    @field_validator("transaction_hash", mode="before")
    @classmethod
    def validate_hash(cls, v: str) -> str:
        return validate_hex(v, 64)

class TransferEvent(BaseModel):
    from_address: Address
    to_address: Address
    value: int = Field(ge=0)
    transaction_hash: Hash32
    block_number: int = Field(ge=0)
    log_index: int = Field(ge=0)

    @field_validator("from_address", "to_address", mode="before")
    @classmethod
    def validate_addresses(cls, v: str) -> str:
        return validate_hex(v, 40)

    @field_validator("transaction_hash", mode="before")
    @classmethod
    def validate_hash(cls, v: str) -> str:
        return validate_hex(v, 64)

class TransactionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    hash: Hash32
    nonce: int = Field(ge=0)
    block_hash: Hash32
    block_number: int = Field(ge=0)
    transaction_index: int = Field(ge=0)
    from_address: Address = Field(alias="from")
    to_address: Optional[Address] = Field(None, alias="to")
    value: int = Field(ge=0)
    gas_price: int = Field(ge=0)
    gas: int = Field(ge=0)
    input: HexData

    @field_validator("hash", "block_hash", mode="before")
    @classmethod
    def validate_hashes(cls, v: str) -> str:
        return validate_hex(v, 64)

    @field_validator("from_address", "to_address", mode="before")
    @classmethod
    def validate_addresses(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return validate_hex(v, 40)

class BlockModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: int = Field(ge=0)
    hash: Hash32
    parent_hash: Hash32
    timestamp: datetime
    miner: Address
    difficulty: int = Field(ge=0)
    total_difficulty: int = Field(ge=0)
    size: int = Field(ge=0)
    extra_data: HexData
    gas_limit: int = Field(ge=0)
    gas_used: int = Field(ge=0)
    base_fee_per_gas: Optional[int] = Field(None, ge=0)

    @field_validator("hash", "parent_hash", mode="before")
    @classmethod
    def validate_hashes(cls, v: str) -> str:
        return validate_hex(v, 64)

    @field_validator("miner", mode="before")
    @classmethod
    def validate_miner(cls, v: str) -> str:
        return validate_hex(v, 40)

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, v: any) -> datetime:
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v)
        return v
